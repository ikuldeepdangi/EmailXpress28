import csv
import re
from io import StringIO
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django import forms
from django.contrib import messages
import PyPDF2
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def MaxFileSizeValidator(max_size):
    def validator(value):
        if value.size > max_size:
            raise ValidationError(f'Maximum file size is {max_size // 1024 // 1024} MB')
    return validator

class EmailForm(forms.Form):
    emails = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter emails separated by commas'}),
        required=False
    )
    email_file = forms.FileField(required=False)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    attachment = forms.FileField(required=False, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'csv']), MaxFileSizeValidator(max_size=5242880)]) 

def extract_emails_from_file(file):
    emails = []
    if file.name.endswith('.txt'):
        content = file.read().decode('utf-8')
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    elif file.name.endswith('.csv'):
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        for row in reader:
            for item in row:
                if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', item):
                    emails.append(item)
    elif file.name.endswith('.pdf'):
        reader = PyPDF2.PdfFileReader(file)
        content = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            content += page.extract_text()
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    return emails

def home_view(request):
    return render(request, 'mailer/home.html')

def sanitize_email(email):
    email = re.sub(r'\s+', '', email)
    if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        return email
    return None

def send_email_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipient_list = form.cleaned_data['emails']
            email_file = request.FILES.get('email_file')
            attachment = request.FILES.get('attachment')

            if email_file:
                file_emails = extract_emails_from_file(email_file)
                recipient_list += ',' + ','.join(file_emails)

            recipient_list = [sanitize_email(email.strip()) for email in recipient_list.split(',') if sanitize_email(email.strip())]
            recipient_list = list(set(recipient_list)) 

            failed_emails = []
            count = 0 

            attachment_content = attachment.read() if attachment else None
            attachment.seek(0) if attachment else None

            try:
                for email in recipient_list:
                    try:
                        email_message = EmailMessage(
                            subject,
                            message,
                            'your_email@example.com',
                            [email]
                        )
                        if attachment_content:
                            email_message.attach(attachment.name, attachment_content, attachment.content_type)
                        
                        email_message.send()
                        print(f"MAIL SENT to {email}")
                        count += 1
                    except Exception as e:
                        print(f"Failed to send email to {email}: {e}")
                        failed_emails.append(email)

                messages.success(request, "Emails sent successfully!")
                print("Total mails sent ->> ", count)
                print("Total mails failed ->> ", len(failed_emails))
                print("TASK COMPLETED")

                if failed_emails:
                    print("Failed to send emails to the following addresses:")
                    for failed_email in failed_emails:
                        print(failed_email)

                return redirect('success')
            except Exception as e:
                messages.error(request, f"Failed to send emails: {e}")
                print("Total mails sent ->> ", count)
                print("Total mails failed ->> ", len(failed_emails))
                print("TASK FAILED")
                return redirect('home')
    else:
        form = EmailForm()
    return render(request, 'mailer/send_email.html', {'form': form})

def success_view(request):
    return render(request, 'mailer/success.html')

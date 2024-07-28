from django import forms

class EmailForm(forms.Form):
    sender_email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
    sender_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Your password'}))
    emails = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter emails separated by commas'}), required=False)
    email_file = forms.FileField(required=False)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    attachment = forms.FileField(required=False)

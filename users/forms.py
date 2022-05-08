from django import forms
from . import models

class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    
    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(username=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                raise forms.ValidationError("Password is wrong!")
        except models.User.DoesNotExist:
            raise forms.ValidationError("User doesn't exist!")


class SignUpForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = (
            "first_name",
            "last_name",
        )
        # 여기 fields에 email이 포함되지 않으면 save() 적용이 안되어 아래에서 수동으로 user.email = email 해줘야 함.
    
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password Confirm")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            models.User.objects.get(email=email)
            raise forms.ValidationError("User already exists")

        except models.User.DoesNotExist:
            return email
    
    def clean_password1(self): # password 를 clean하면 순차적으로 진행되는 특성상 password1은 아직 cleaned_data로 넘어오지 않아서 password1으로 clean해야 함. 
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")

        if password != password1:
            raise forms.ValidationError("Password cofirmation doesn't match!")
        else:
            return password

    def save(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = super().save(commit=False) 
        user.username = email
        user.set_password(password)
        user.email = email
        user.save()


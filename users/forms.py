from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from . import models

class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    # Form 클래스를 상속한 경우 위젯의 속성을 통해서 input을 컨트롤한다. 
    
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
        # ModelForm 클래스 상속의 경우 여기 fields에 email이 포함되지 않으면 save() 적용이 안되어 아래에서 수동으로 user.email = email 해줘야 함.
        fields = (
            "first_name",
            "last_name",
        )
       # ModelForm 클래스 상속의 경우 Meta 클래스에서 필드를 명시하여 사용하는 경우 위젯은 아래와 같이 작성한다. 
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Frst Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name"}),
        }
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}), label="Password Confirm")

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
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error(None, error)
            return password

    def save(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = super().save(commit=False) 
        user.username = email
        user.set_password(password)
        user.email = email
        user.save()


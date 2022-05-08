from xml.dom import ValidationErr
from django.forms import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.template.loader import render_to_string
from django.views.generic import FormView
from django.contrib.auth import login, logout, authenticate
from . import forms, models


class LoginView(FormView):
    
    form_class = forms.LoginForm
    template_name = "users/login.html"
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):

    form_class = forms.SignUpForm	
    template_name = "users/signup.html"
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save() # 이걸 안하면 form에서 save()한게 진행되지 않음. 
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        print(self.request)
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            user.verify_email()
            html_message = render_to_string("emails/request_email.html", context={"email":user.email})
            return HttpResponse(html_message)
        return super().form_valid(form)

def email_confirmation(request, secret):
    try:
        user = models.User.objects.get(email_secret=secret)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        login(request, user)
        # to do: add success message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))

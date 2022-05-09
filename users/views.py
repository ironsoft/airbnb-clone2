import os
import requests
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

def github_login(request):
    client_id = os.environ.get("GITHUB_ID")
    redirect_url = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_url={redirect_url}&scope=read:user")


class GitHubException(Exception):
    pass

def github_callback(request):
    try:
        code = request.GET.get("code", None) # None 처리를 안해주면 code를 받지 못하는 경우 error가 날 수 있다.
        client_id = os.environ.get("GITHUB_ID")
        client_secret = os.environ.get("GITHUB_SECRET")
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"}
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GitHubException()
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get("https://api.github.com/user", 
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json"
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    try:
                        user = models.User.objects.get(email=email)
                        # 이 메일을 사용한 user가 이미 있으면 둘중 하나지 기존에 깃헙으로 가입되어 있으니 로그인 시켜주던가 아니면 이 가입자가 다른 방식으로 이미 가입되어 있으니 그쪽으로 가서 로그인하라던가
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GitHubException()
                        # 이미 가입자의 경우 로그인 시켜 주는데 신규가입과 공통이므로 아래 로그인 부분과 redirect 부분을 앞으로 빼준다. 
                    except models.User.DoesNotExist:
                        # 신규가입임으로 user 생성해줌. 
                        user = models.User.objects.create(
                            username=email,
                            first_name=name,
                            bio=bio,
                            email=email,
                            login_method=models.User.LOGIN_GITHUB,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    return redirect(reverse("core:home"))
                else:
                    raise GitHubException()
        else:
            raise GitHubException()

    except GitHubException:
        # send error message
        return redirect(reverse("users:login"))
import os
import requests
from django.forms import forms
from django.utils import translation
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.template.loader import render_to_string
from django.views.generic import FormView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordChangeView
from django.core.files.base import ContentFile
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):
    
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
    
    def get_success_url(self) -> str:
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return redirect(reverse("core:home"))
        


def log_out(request):
    logout(request)
    messages.info(request, "See you later")
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
                raise GitHubException("Can't get authorization code.")
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
                            raise GitHubException(f"Please log in with {user.login_method}")
                        # 이미 가입자의 경우 로그인 시켜 주는데 신규가입과 공통이므로 아래 로그인 부분과 redirect 부분을 앞으로 빼준다. 
                    except models.User.DoesNotExist:
                        # 신규가입임으로 user 생성해줌. 
                        user = models.User.objects.create(
                            username=email,
                            first_name=name,
                            bio=bio,
                            email=email,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome, {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GitHubException("Can't get your profile!")
        else:
            raise GitHubException("Something went wrong!")

    except GitHubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    client_id = os.environ.get("KAKAO_KEY")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code")

class KakaoException(Exception):
    pass

def kakao_callback(request):
    try:
        code = request.GET.get("code", None)
        if code is None:
            raise KakaoException("Something went wrong!")        
        client_id = os.environ.get("KAKAO_KEY")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.post(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}", headers={
            "Content-type": "application/json"
        })
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can't get authorization code.")   
        access_token = token_json.get("access_token")
        profile_request = requests.get("https://kapi.kakao.com//v2/user/me", headers={
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/json"
        })
        profile_json = profile_request.json()
        profile = profile_json.get("kakao_account")
        email = profile.get("email", None)
        if email is None:
            raise KakaoException("Please also give me your email!")
        properties = profile_json.get("properties")
        nickname = properties.get("nickname", None)
        profile_image = properties.get("profile_image", None)
        
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please log in with {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                username=email,
                first_name=nickname,
                email=email,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True
            )
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(f"{nickname}-avatar", ContentFile(photo_request.content))
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}")
        return redirect(reverse("core:home"))


    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))



class UserProfileView(DetailView):
    
    model = models.User
    context_object_name = 'user_obj'


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    
    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )

    success_message = "Profile updated successfully!"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        self.object.username = email
        self.object.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['email'].widget.attrs = {"placeholder": "Email"}
        form.fields['first_name'].widget.attrs = {"placeholder": "First Name"}
        form.fields['last_name'].widget.attrs = {"placeholder": "Last Name"}
        form.fields['gender'].widget.attrs = {"placeholder": "Gender"}
        form.fields['bio'].widget.attrs = {"placeholder": "Bio"}
        form.fields['birthdate'].widget.attrs = {"placeholder": "Birthdate"}
        form.fields['language'].widget.attrs = {"placeholder": "Language"}
        form.fields['currency'].widget.attrs = {"placeholder": "Currency"}
        return form
    

class UpdatePasswordView(mixins.LoggedInOnlyView, mixins.EmailLoginOnlyView, PasswordChangeView):
    
    template_name = 'users/update-password.html'
    success_url = reverse_lazy('users:profile')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['old_password'].widget.attrs = {"placeholder": "Current Password"}
        form.fields['new_password1'].widget.attrs = {"placeholder": "New Password"}
        form.fields['new_password2'].widget.attrs = {"placeholder": "Confirm New Password"}
        return form
    
    def get_success_url(self) -> str:
        messages.success(self.request, "Password Changed Successfully!")
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse('core:home'))


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        translation.activate(lang)
        response = HttpResponse(status=200) 
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    
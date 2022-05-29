from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.log_out, name="logout"),
    path("login/github/", views.github_login, name="github-login"),
    path("login/github/callback", views.github_callback, name="github-callback"),
    path("login/kakao/", views.kakao_login, name="kakao-login"),
    path("login/kakao/callback", views.kakao_callback, name="kakao-callback"), #callback 뒤에는 /를 붙이면 안됐던 기억이...
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("verify/<str:secret>/", views.email_confirmation, name="verify"),
    path("<int:pk>/", views.UserProfileView.as_view(), name="profile"),
    path("profile-update/", views.UpdateProfileView.as_view(), name="profile-update"),
    path("update-password/", views.UpdatePasswordView.as_view(), name="update-password"),
]

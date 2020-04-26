from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from vote import forms
from vote import views

urlpatterns = [
    path('', views.index, name='index'),

    # code login
    path('code', auth_views.LoginView.as_view(
        authentication_form=forms.AccessCodeAuthenticationForm,
        template_name='vote/login.html'
    ), name='code_login'),
    path('code/', RedirectView.as_view(pattern_name='code_login')),
    path('code/<str:access_code>', views.code_login),
    path('logout', auth_views.LogoutView.as_view(
        next_page='index',
    ), name='logout'),

    # voting
    path('vote', views.vote, name='vote'),

    # applications
    path('application', views.upload_application, name='upload_application'),
    path('application/', RedirectView.as_view(pattern_name='upload_application')),
    path('application/<pk>', views.view_application, name='view_application')
]

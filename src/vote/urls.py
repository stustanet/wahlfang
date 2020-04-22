from django.urls import path
from django.contrib.auth import views as auth_views

from vote import forms
from vote import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vote', views.vote, name='vote')
]

# account management stuff
urlpatterns += [
    path('login', auth_views.LoginView.as_view(
        authentication_form=forms.TokenAuthenticationForm,
        template_name='vote/login.html'
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='index',
    ), name='logout')
]

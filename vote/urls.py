from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView

from vote import views

app_name = 'vote'

urlpatterns = [
    path('', views.index, name='index'),
    path('vote/<int:election_id>', views.vote, name='vote'),

    # code login
    path('code', views.LoginView.as_view(), name='code_login'),
    path('code/', RedirectView.as_view(pattern_name='code_login')),
    path('code/<str:access_code>', views.code_login, name='link_login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='vote:index',
    ), name='logout'),
    path('vote/<int:election_id>/apply', views.apply, name='apply'),
    path('vote/<int:election_id>/delete-own-application', views.delete_own_application, name='delete_own_application'),
    path('help', views.help_page, name='help'),
    path('spectator/<str:uuid>', views.spectator, name='spectator')
]

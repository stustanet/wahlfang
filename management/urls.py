from django.urls import path,re_path
from django.contrib.auth import views as auth_views

from management import views

app_name = 'management'

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'meeting/(?P<pk>\d+)/add_voters', views.add_voters, name='add_voters'),
    re_path(r'meeting/(?P<pk>\d+)/add_election', views.add_election, name='add_election'),
    re_path(r'meeting/(?P<pk>\d+)', views.session, name='session'),
    re_path(r'election/(?P<pk>\d+)/add_application', views.election_upload_application, name='add_application'),
    re_path(r'election/(?P<pk>\d+)/edit/(?P<application_id>\d+)', views.election_upload_application, name='edit_application'),
    re_path(r'election/(?P<pk>\d+)', views.election, name='election'),

    # account management stuff
    path('login', auth_views.LoginView.as_view(
        template_name='management/login.html'
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='management:login',
    ), name='logout')
]

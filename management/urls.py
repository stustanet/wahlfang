from django.contrib.auth import views as auth_views
from django.urls import path

from management import views

app_name = 'management'

urlpatterns = [
    path('', views.index, name='index'),
    path('meeting/<int:pk>/add_voters', views.add_voters, name='add_voters'),
    path('meeting/<int:pk>/add_tokens', views.add_tokens, name='add_tokens'),
    path('meeting/<int:pk>/add_election', views.add_election, name='add_election'),
    path('meeting/<int:pk>', views.session_detail, name='session'),
    path('election/<int:pk>/add_application', views.election_upload_application, name='add_application'),
    path('election/<int:pk>/edit/<int:application_id>', views.election_upload_application, name='edit_application'),
    path('election/<int:pk>/edit/<int:application_id>/delete_application', views.election_delete_application,
         name='delete_application'),
    path('election/<int:pk>', views.election_detail, name='election'),
    path('election/<int:pk>/delete_voter', views.delete_voter, name='delete_voter'),
    path('election/<int:pk>/delete_election', views.delete_election, name='delete_election'),
    path('meeting/<int:pk>/delete_session', views.delete_session, name='delete_session'),
    path('meeting/<int:pk>/print_token', views.print_token, name='print_token'),

    # account management stuff
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='management:login',
    ), name='logout')
]

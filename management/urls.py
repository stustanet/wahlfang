from django.urls import path
from django.contrib.auth import views as auth_views

from management import views

app_name = 'management'

urlpatterns = [
    path('', views.index, name='index'),
    path('election/<int:pk>', views.election, name='election'),
    path('election/<int:pk>/add_voters', views.election_add_voters, name='election_add_voters'),
    path('add_election/', views.add_election, name='add_election'),
    path('election/<int:pk>/application', views.election_upload_application, name='election_upload_application'),
    path('election/<int:pk>/application/<int:application_id>',
         views.election_upload_application, name='election_edit_application'),

    # account management stuff
    path('login', auth_views.LoginView.as_view(
        template_name='management/login.html'
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='management:login',
    ), name='logout')
]

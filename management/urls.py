from django.urls import path
from django.contrib.auth import views as auth_views

from management import views

app_name = 'management'

urlpatterns = [
    path('', views.index, name='index'),
    path('election/<int:pk>', views.election, name='election'),
    path('election/<int:pk>/add_voters', views.election_add_voters, name='election_add_voters'),
    path('election/<int:pk>/add_application', views.election_add_application, name='election_add_application'),
    path('election/<int:pk>/<str:action>', views.election, name='election_action'),
    path('add_election/', views.add_election, name='add_election'),

    # account management stuff
    path('login', auth_views.LoginView.as_view(
        template_name='management/login.html'
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='management:login',
    ), name='logout')
]

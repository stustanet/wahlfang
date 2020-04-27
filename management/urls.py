from django.urls import path
from django.contrib.auth import views as auth_views

from management import views

app_name = 'management'

urlpatterns = [
    path('', views.index, name='index'),
    path('election_result/<int:pk>', views.election_result, name='election_result'),
]

# account management stuff
urlpatterns += [
    path('login', auth_views.LoginView.as_view(
        template_name='management/login.html'
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='management:login',
    ), name='logout')
]

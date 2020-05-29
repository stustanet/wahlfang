from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from vote import views

app_name = 'vote'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:election>', views.index, name='index'),

    # code login
    path('code', views.LoginView.as_view(), name='code_login'),
    path('code/', RedirectView.as_view(pattern_name='code_login')),
    path('code/<str:access_code>', views.code_login, name='link_login'),
    path('logout', auth_views.LogoutView.as_view(
        next_page='vote:index',
    ), name='logout'),
]

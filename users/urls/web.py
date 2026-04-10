from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .. import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.RegisterWebView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:home'), name='logout'),
    path('profile/', views.ProfileWebView.as_view(), name='profile'),
]

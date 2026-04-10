from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, UserPreferences
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserPreferencesForm
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserPreferencesSerializer


# ============================================================================
# API VIEWS
# ============================================================================

class RegisterView(APIView):
    """API view for user registration."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful. Please verify your email.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """API view for user login."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API view for user logout."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Token blacklisting handled by simplejwt
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """API view for user profile retrieval."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        preferences = user.preferences if hasattr(user, 'preferences') else None
        return Response({
            'user': UserSerializer(user).data,
            'preferences': UserPreferencesSerializer(preferences).data if preferences else None,
        }, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    """API view for updating user profile."""
    
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# WEB VIEWS
# ============================================================================

class RegisterWebView(CreateView):
    """Web view for user registration."""
    
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)


class ProfileWebView(LoginRequiredMixin, TemplateView):
    """Web view for user profile."""
    
    template_name = 'accounts/profile.html'
    login_url = 'auth:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['preferences'] = getattr(user, 'preferences', None)
        context['profile_form'] = CustomUserChangeForm(instance=user)
        context['preferences_form'] = UserPreferencesForm(instance=user.preferences) if hasattr(user, 'preferences') else None
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        
        if 'profile_update' in request.POST:
            form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect('auth:profile')
        
        elif 'preferences_update' in request.POST:
            preferences = getattr(user, 'preferences', None)
            if preferences:
                form = UserPreferencesForm(request.POST, instance=preferences)
                if form.is_valid():
                    form.save()
                    return redirect('auth:profile')
        
        return self.get(request, *args, **kwargs)

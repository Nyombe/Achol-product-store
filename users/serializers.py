from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserPreferences


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model."""
    
    full_name = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'profile_picture',
            'street_address', 'city', 'state', 'postal_code', 'country',
            'full_address', 'is_verified', 'email_verified', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'is_verified', 'email_verified', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_full_address(self, obj):
        return obj.get_full_address()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Email already in use.'})
        
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        UserPreferences.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Invalid email or password.')

        return attrs


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    class Meta:
        model = UserPreferences
        fields = (
            'email_notifications', 'sms_notifications', 'order_updates',
            'promotional_emails', 'show_profile', 'allow_data_collection',
            'preferred_currency', 'preferred_language', 'theme', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

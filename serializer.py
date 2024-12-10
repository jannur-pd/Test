from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import *


class ArtUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
        read_only_fields = ['id', 'is_active', 'is_staff']

    def create(self, validated_data):

        password = validated_data.pop('password', None)
        user = ArtUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = ArtUser
        fields = ['email', 'first_name', 'last_name', 'role', 'password']

    def validate_email(self, value):

        if ArtUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):

        password = validated_data.pop('password')
        user = ArtUser(**validated_data)
        user.set_password(password)  # хэшируем пароль
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtUser
        fields = ['first_name', 'last_name', 'role', 'email']

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name']


class NicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Niche
        fields = ['name']

class PhotographerSerializer(serializers.ModelSerializer):
    user = None #ArtUserSerializer()
    languages_spoken = LanguageSerializer(many=True)
    country = serializers.CharField(source='country.name')
    niche = serializers.CharField(source='niche.name')

    class Meta:
        model = Photographer
        fields = ['id', 'first_name', 'last_name', 'country', 'niche', 'price_per_hour', 'languages_spoken', 'available_for_international']

class ProfilePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ['profile_picture']


class PhotoSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer()

    class Meta:
        model = Portfolio
        fields = ['id', 'photographer', 'image', 'description']

class ReviewSerializer(serializers.ModelSerializer):
    client = ArtUserSerializer()
    photographer = PhotographerSerializer()

    class Meta:
        model = Review
        fields = ['id', 'client', 'photographer', 'rating', 'comment']
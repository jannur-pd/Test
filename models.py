from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
import requests

class ArtUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(email=username)

class ArtUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=[('photographer', 'Photographer'), ('client', 'Client')])


    objects = ArtUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

class Language(models.Model):
    name = models.CharField(max_length=101)
    def __str__(self):
        return self.name

class Photographer(models.Model):
    user = models.OneToOneField(ArtUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=101)
    last_name = models.CharField(max_length=101)
    email = models.EmailField(unique=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=255, blank=True)
    niche = models.ForeignKey('Niche', on_delete=models.SET_NULL, null=True)
    instagram = models.URLField(max_length=2000, null=True, blank=True)
    languages_spoken = models.ManyToManyField(Language)
    price_per_hour = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to='photographers', null=True, blank=True)
    portfolio = models.ImageField(upload_to='portfolio', null=True, blank=True)
    available_for_international = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Country(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Niche (models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Client(models.Model):
    user = models.OneToOneField(ArtUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=101)
    last_name = models.CharField(max_length=101)
    orders = models.ForeignKey('Order',  on_delete=models.SET_NULL, related_name='client_orders', null=True, blank=True)
    def __str__(self):
        return f"{self.first_name}"


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders_set')
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    total_cost = models.IntegerField(default=0)
    def __str__(self):
        return f"Order {self.id} for {self.client}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        client_name = self.client.user.first_name if self.client.user else "Unknown Client"
        photographer_name = self.photographer.user.first_name if self.photographer.user else "Unknown Photographer"
        return f"Review by {client_name} for {photographer_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        reviews = Review.objects.filter(photographer=self.photographer)
        average = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.photographer.average_rating = average
        self.photographer.save(update_fields=['average_rating'])



class Portfolio(models.Model):
    photographer = models.ForeignKey(Photographer, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')
    description = models.TextField()

    def __str__(self):
        return f"Photo by {self.photographer.user.first_name}"


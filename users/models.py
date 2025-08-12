from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    PROFESSEUR = 'professeur'
    ROLE_CHOICES = [
        (ADMIN, 'Administrateur'),
        (PROFESSEUR, 'Professeur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ADMIN)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

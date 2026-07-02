from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        AUTHOR = 'author', 'Author'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER, verbose_name='User Role')
    bio = models.TextField(blank=True, null=True, verbose_name='Biography')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    job = models.CharField(max_length=100, blank=True, null=True, verbose_name='job')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Phone Number')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date of birth')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username



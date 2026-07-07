from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


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
    following = models.ManyToManyField('self', through='UserFollow', related_name='followers', symmetrical=False,
                                       verbose_name='Following')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date of birth')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_absolute_url(self):
        return reverse('accounts:user_detail', args=[self.username])

    def __str__(self):
        return self.username


class Contact(models.Model):
    message = models.TextField(verbose_name='Message text')
    name = models.CharField(max_length=100, verbose_name='Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=11, verbose_name='Phone Number')
    subject = models.CharField(max_length=100, verbose_name='Subject')

    class Meta:
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us'

    def __str__(self):
        return self.subject


class UserFollow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations',
                                 verbose_name='Follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations',
                                  verbose_name='Following')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Follower'
        verbose_name_plural = 'Followers'

    def __str__(self):
        return f'{self.follower} follows {self.following}'

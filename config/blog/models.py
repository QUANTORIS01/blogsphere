import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from bs4 import BeautifulSoup
from django.conf import settings
from taggit.managers import TaggableManager
from accounts.models import User


class DraftManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.DRAFT)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.PUBLISH)


class RejectedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.REJECT)


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('Technology', 'Technology'),
        ('Programming', 'Programming'),
        ('Design', 'Design'),
        ('Database', 'Database'),
        ('AI', 'AI'),
        ('Blockchain', 'Blockchain'),
        ('Other', 'Other'),
    ]

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISH = 'PB', 'Published'
        REJECT = 'RJ', 'Rejected'

    title = models.CharField(max_length=100, verbose_name='Title')
    banner = models.ImageField(upload_to='banners/', null=True, blank=True, verbose_name='Banner')
    description = models.TextField(verbose_name='Description')
    category = models.CharField(choices=CATEGORY_CHOICES, default='Other', verbose_name='Category')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Publication Date')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    updated = models.DateTimeField(auto_now=True, verbose_name='Last updated')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Status')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts', verbose_name='Author')
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True, verbose_name='Saved by')
    tags = TaggableManager(verbose_name='Tags')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name='Likes')
    total_likes = models.PositiveIntegerField(default=0, verbose_name='Number of likes')
    read_time = models.PositiveIntegerField(default=0, verbose_name='Reading time')
    visits = models.PositiveIntegerField(default=0, verbose_name='Number of views')
    objects = models.Manager()
    published = PublishedManager()
    rejected = RejectedManager()
    draft = DraftManager()

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.pk])

    def delete(self, *args, **kwargs):
        if self.banner and os.path.isfile(self.banner.path):
            self.banner.delete(save=False)
        if self.description:
            soup = BeautifulSoup(self.description, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    if src.startswith('/media/'):
                        file_path = src[7:]
                        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ('-publish',)
        indexes = [
            models.Index(fields=['-publish']),
            models.Index(fields=['-total_likes'])
        ]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from bs4 import BeautifulSoup
from django.conf import settings
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
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
    description = CKEditor5Field(config_name='extends', verbose_name='Description')
    category = models.CharField(choices=CATEGORY_CHOICES, default='Other', verbose_name='Category')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Publication Date')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    updated = models.DateTimeField(auto_now=True, verbose_name='Last updated')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Status')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts', verbose_name='Author')
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True, verbose_name='Saved by')
    tags = TaggableManager(verbose_name='Tags')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name='Likes')
    reason_rejected = models.TextField(null=True, blank=True, verbose_name='Reason for rejection')
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


class AuthorRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_requests', verbose_name='Name')
    full_name = models.CharField(max_length=99, verbose_name='Full name')
    email = models.EmailField(max_length=99, verbose_name='Email')
    phone = models.CharField(max_length=11, verbose_name='Phone Number')
    national_id = models.CharField(max_length=10, verbose_name='National ID Number')
    description = models.TextField(max_length=499, verbose_name='Description')
    resume = models.FileField(upload_to='author_resumes/', verbose_name='Resume')
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.PENDING, verbose_name='Status')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_author_requests', verbose_name='Reviewed by')
    rejection_reason = models.TextField(max_length=499, blank=True, null=True, verbose_name='Reason for rejection')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    reviewed = models.DateTimeField(blank=True, null=True, verbose_name='Review Date')
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='locked_author_requests', verbose_name='Locked by')
    locked_at = models.DateTimeField(blank=True, null=True, verbose_name='Lock Date')

    class Meta:
        verbose_name = 'Writing Application'
        verbose_name_plural = 'Writing Requests'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return f'{self.user.username} - {self.status}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Post')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments',
                             verbose_name='Author')
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Guest Name')
    body = models.TextField(verbose_name='Comment text')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                               verbose_name='Response to')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    updated = models.DateTimeField(auto_now=True, verbose_name='Last updated')
    level = models.PositiveIntegerField(default=0, verbose_name='Conceptual level')

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
        verbose_name = 'Opinion'
        verbose_name_plural = 'Comments'

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user:
            return f'{self.user.username}: {self.post}'
        return f'{self.name}: {self.post}'

    def get_all_replies(self):
        replies = []
        for reply in self.replies.all():
            replies.append(reply)
            replies.extend(reply.get_all_replies())
        return replies

    def can_reply(self):
        return self.level < 4

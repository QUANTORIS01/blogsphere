from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Post


@receiver(m2m_changed, sender=Post.likes.through)
def users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()


@receiver(post_delete, sender=Post)
def email_users_when_post_deleted(sender, instance, **kwargs):
    author = instance.author
    subject = f'Post {instance.title} Removed'
    message = (f'{author} Sorry, but post.'
               f'<< {instance.title} >>'
               f'It was removed for a number of reasons. You can check the tickets section to find out why.')
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [author.email], fail_silently=False)

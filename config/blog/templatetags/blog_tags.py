from django import template
from django.db.models import Count
from ..models import Post

register = template.Library()


@register.inclusion_tag('blog/Home/latest_posts.html')
def latest_posts(count=3):
    latest_post_list = Post.published.order_by('-publish')[:count]

    context = {
        'l_posts': latest_post_list
    }
    return context


@register.inclusion_tag('blog/Home/popular_posts.html')
def popular_posts(count=3):
    popular_post_list = Post.published.annotate(
        popular_count=Count('likes')
    ).order_by('-popular_count')[:count]
    context = {
        'p_posts': popular_post_list
    }
    return context


@register.inclusion_tag('blog/Home/active_author.html')
def active_author(count=3):
    active_authors = Post.published.values(
        'author__username',
        'author__id',
    ).annotate(
        post_count=Count('author')
    ).order_by('-post_count')[:count]

    for author in active_authors:
        try:
            from django.contrib.auth.models import User
            from ..models import Intermediary
            user = User.objects.get(id=author['author__id'])
            if hasattr(user, 'account') and user.account.avatar:
                author['avatar_url'] = user.account.avatar.url
            else:
                author['avatar_url'] = None

            follower_count = Intermediary.objects.filter(user_to=user).count()
            author['follower_count'] = follower_count
        except:
            author['avatar_url'] = None
            author['follower_count'] = 0

    context = {
        'active_authors': active_authors
    }
    return context


@register.filter(name='secure_truncate')
def secure_truncate(value, length=110):
    try:
        import re
        from django.utils.html import strip_tags
        clean_value = re.sub(r'(&nbsp;|\u00A0|\s)+', ' ', value)
        clean_value = strip_tags(clean_value)
        clean_value = re.sub(r'\s+', ' ', clean_value).strip()
        if len(clean_value) > length:
            clean_value = clean_value[:length].rsplit(' ', 1)[0] + ' ...'

        return clean_value
    except:
        return value[:length] + ' ...' if len(value) > length else value


from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, F
from .models import *


def index(request):
    posts = Post.published.all()
    context = {'posts_view': posts}
    return render(request, 'blog/Home/Home.html', context)


def post_list(request, category=None):
    if category is not None:
        posts = Post.published.filter(category=category)
    else:
        posts = Post.published.select_related('author').order_by('-total_likes')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.get_page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    context = {
        'posts': posts,
        'category': category,
    }
    return render(request, 'blog/Post_list/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISH)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_post = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:4]
    visit_post = request.session.get('visit_post', [])
    if post.pk not in visit_post:
        post.visits = F('visits') + 1
        post.save(update_fields=['visits'])
        visit_post.append(post.pk)
        request.session['visit_post'] = visit_post
        post.refresh_from_db()
    context = {
        'post': post,
        'similar_post': similar_post,
        'model_name': 'blog.post',
        'object_id': post.pk,
    }
    return render(request, 'blog/Detail/post_detail.html', context)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        post_likes_count = post.likes.count()
        response_data = {
            'liked': liked,
            'post_likes_count': post_likes_count
        }
    else:
        response_data = {
            'error': 'Invalid post id'
        }
    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = Post.objects.get(pk=post_id)
        user = request.user
        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True
        return JsonResponse({'saved': saved})
    return JsonResponse({'error': 'Invalid post id'})



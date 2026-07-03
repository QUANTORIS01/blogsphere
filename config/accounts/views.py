from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from blog.models import Post
from .forms import *


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            context = {
                'user': user
            }
            return render(request, 'registration/register_done.html', context)
    else:
        form = UserRegisterForm()
    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


def log_out(request):
    logout(request)
    return redirect('blog:index')


def dashboard_admin(request):
    all_post = Post.objects.all()
    post_user = Post.objects.filter(author=request.user)
    post_published = Post.published.all()
    post_draft = Post.draft.all()
    post_rejected = Post.rejected.all()
    like_post = Post.objects.filter(likes=request.user)
    context = {
        'all_post': all_post,
        'post_user': post_user,
        'post_published': post_published,
        'post_draft': post_draft,
        'post_rejected': post_rejected,
        'like_post': like_post,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


def dashboard_author(request):
    post_published = Post.published.filter(author=request.user)
    post_draft = Post.draft.filter(author=request.user)
    post_rejected = Post.rejected.filter(author=request.user)
    like_post = Post.objects.filter(likes=request.user)
    saved_posts = Post.objects.filter(saved_by=request.user)
    context = {
        'post_published': post_published,
        'post_draft': post_draft,
        'post_rejected': post_rejected,
        'like_post': like_post,
        'saved_posts': saved_posts,
    }
    return render(request, 'dashboard/author_dashboard.html', context)


def dashboard_user(request):
    liked_posts = Post.objects.filter(likes=request.user)
    saved_posts = Post.objects.filter(saved_by=request.user)
    context = {
        'liked_posts': liked_posts,
        'saved_posts': saved_posts,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@login_required()
def dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return dashboard_admin(request)
    elif request.user.role == User.Role.AUTHOR:
        return dashboard_author(request)
    else:
        return dashboard_user(request)
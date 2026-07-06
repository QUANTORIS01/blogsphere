import jdatetime
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.core.files.storage import default_storage
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, F, Q
from django.utils import timezone
from accounts.email_service import send_email_thread
from .forms import *
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
    tags = Post.tags.all()
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
        'tags': tags,
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


@login_required
def create_post(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('accounts:dashboard')
    else:
        form = CreatePostForm()
    return render(request, 'forms/create_post.html', {'form': form})


@login_required
def edit_post(request, post_id):
    author_post = Post.objects.filter(author=request.user)
    post = get_object_or_404(author_post, id=post_id)
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == Post.Status.REJECT:
                post.status = Post.Status.DRAFT
            post.save()
            return redirect('accounts:dashboard')
    else:
        form = CreatePostForm(instance=post)
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'forms/create_post.html', context)


@login_required
def delete_post(request, post_id):
    user_non_published_posts = Post.draft.filter(author=request.user) | Post.rejected.filter(author=request.user)
    post = get_object_or_404(user_non_published_posts, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('accounts:dashboard')
    return render(request, 'forms/delete_post.html', {'post': post})


@login_required
@require_POST
def secure_ckeditor_upload(request):
    user = request.user
    if user.role not in ['admin', 'author']:
        return HttpResponseForbidden('You are not allowed to upload images.')
    upload = request.FILES.get('upload')
    if not upload:
        return JsonResponse({'error': 'No file has been sent.'}, status=400)
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(upload.name)[1].lower()
    if ext not in allowed_extensions:
        return JsonResponse({'error': 'Invalid file format.'}, status=400)
    max_size = 5 * 1024 * 1024
    if upload.size > max_size:
        return JsonResponse({'error': 'The file size exceeds 5 MB.'}, status=400)
    username = user.username
    today_solar = jdatetime.date.today().strftime('%Y/%m/%d')
    filename = f'{uuid.uuid4().hex}{ext}'
    upload_path = os.path.join('uploads', 'ckeditor', username, today_solar, filename)
    saved_path = default_storage.save(upload_path, upload)
    file_url = default_storage.url(saved_path)
    return JsonResponse({'uploaded': True, 'url': file_url})


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.filter(Q(title__icontains=query) | Q(description__icontains=query))
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'blog/search.html', context)


@login_required
def request_authorship(request):
    user = request.user
    if not user.is_authenticated:
        messages.info(request, 'You are not allowed to request a pending request')
    if user.role != User.Role.USER:
        messages.error(request, 'You cannot submit a request.')
    if not is_account_complete(user):
        messages.error(request, 'Please complete your information.')
    if AuthorRequest.objects.filter(user=request.user, status=AuthorRequest.Status.PENDING).exists():
        messages.info(request, 'You have a pending request!!! Please wait for a response.')
    if request.method == 'POST':
        form = AuthorRequestForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                author_request = form.save(commit=False)
                author_request.user = request.user
                author_request.full_name = f'{request.user.first_name} {request.user.last_name}'
                author_request.email = request.user.email
                author_request.phone = user.phone
                author_request.save()
                send_email_thread(
                    'Your request is being processed.',
                    'You will be informed of the result after the review. '
                    'Thank you.',
                    [author_request.email],
                )
                messages.success(request, 'Your request has been successfully submitted.')
    else:
        form = AuthorRequestForm(initial={
            'full_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
            'email': request.user.email,
            'phone': user.phone,
        })
        form.fields['full_name'].widget.attrs['readonly'] = True
        form.fields['email'].widget.attrs['readonly'] = True
        form.fields['phone'].widget.attrs['readonly'] = True
    return render(request, 'forms/author_request.html', {'form': form})


def is_account_complete(user):
    return all([
        user.first_name,
        user.last_name,
        user.email,
        user.phone,
    ])


@login_required
def review_author_request(request, request_id):
    user = request.user
    if user.role != User.Role.ADMIN:
        messages.error(request, 'You do not have permission to access this section.')
        return redirect('accounts:dashboard')

    with transaction.atomic():
        # Locking a record to prevent concurrent access
        author_request = AuthorRequest.objects.select_for_update().get(id=request_id)

        # Checking lock status
        if author_request.locked_by and author_request.locked_by != request.user:
            messages.error(request,
                           f'This request is currently being processed by {author_request.locked_by.get_full_name() or author_request.locked_by.username}It is under review.')

        # Checking application status
        if author_request.status != AuthorRequest.Status.PENDING:
            messages.error(request, 'This request has already been reviewed.')
            return redirect('accounts:dashboard')

        # Locking the request by the current user
        if not author_request.locked_by:
            author_request.locked_by = request.user
            author_request.locked_at = timezone.now()
            author_request.save()

        if request.method == 'POST':
            # Unlock after review completion
            author_request.locked_by = None
            author_request.locked_at = None
            status = request.POST.get('status')
            rejection_reason = request.POST.get('rejection_reason')
            author_request.status = status
            author_request.reviewed_by = request.user
            author_request.rejection_reason = rejection_reason
            author_request.reviewed = timezone.now()
            author_request.save()

            if status == AuthorRequest.Status.APPROVED:
                user_account = author_request.user
                user_account.role = User.Role.AUTHOR
                user_account.save()
                send_email_thread(
                    'Your request to become a writer has been approved.',
                    'Your authorship has been approved, and your role has been changed to Author.'
                    'Thank you.',
                    [author_request.email],
                )
            elif status == AuthorRequest.Status.REJECTED:
                send_email_thread(
                    'Your application to become a writer has been rejected!!!',
                    f'Unfortunately, your request to become a writer has been rejected.\nReason:\n{rejection_reason}',
                    [author_request.email],
                )
            messages.success(request, 'The review was successfully completed.')
            return redirect('accounts:dashboard')

    return render(request, 'forms/review_author_request.html', {'author_request': author_request})


@login_required
def pending_requests(request):
    user = request.user
    if not user.is_authenticated:
        messages.info(request, 'You are not allowed to access this section.')
    if user.role not in [User.Role.ADMIN]:
        messages.error(request, 'You do not have permission to access this section.')
        return redirect('blog:home')
    pending_requests_list = AuthorRequest.objects.filter(
        status=AuthorRequest.Status.PENDING
    ).exclude(locked_by__isnull=False).exclude(locked_by=request.user)
    return render(request, 'forms/pending_requests.html', {'pending_requests_list': pending_requests_list})


@login_required
def all_author_requests(request):
    account = request.user
    if not account.is_authenticated:
        messages.info(request, 'You are not allowed to access this section.')
    if account.role not in [User.Role.ADMIN]:
        messages.error(request, 'You do not have permission to access this section.')
        return redirect('blog:home')
    all_requests = AuthorRequest.objects.all().order_by('-created')
    return render(request, 'forms/all_author_requests.html', {'all_requests': all_requests})

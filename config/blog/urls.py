from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<str:category>/', views.post_list, name='post_list_category'),
    path('posts/detail/<int:pk>/', views.post_detail, name='post_detail'),
    path('like-post/', views.like_post, name='like_post'),
    path('save-post/', views.save_post, name='save_posts'),
    path('dashboard/create-post', views.create_post, name='create_post'),
    path('dashboard/create-post/<post_id>', views.edit_post, name='edit_post'),
    path('dashboard/delete-post/<post_id>', views.delete_post, name='delete_post'),
    path('ckeditor/upload/', views.secure_ckeditor_upload, name='secure_ckeditor_upload'),
    path('search/', views.post_search, name='post_search'),
    path('request-authorship/', views.request_authorship, name='request_authorship'),
    path('review-request/<int:request_id>/', views.review_author_request, name='review_author_request'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('author-requests/', views.all_author_requests, name='all_author_requests'),
]

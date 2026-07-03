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
    
]

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

]

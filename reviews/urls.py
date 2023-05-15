from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('like-unlike-post/', views.like_unlike_post, name='like_unlike_post'),
    path('create-post/', views.create_post, name='create_post'),
    path('settings/', views.settings_view, name='settings'),
    path('posts/signing/', views.signing, name='signing'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('accounts/profile/', views.profile_view),
    path('posts/', views.post_list, name='post_list'),
    path('posts/profile_bef/', views.profile_view, name='profile'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_pk>/comments/new/', views.comment_edit, name='comment_create'),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/', views.comment_edit, name='comment_edit'),
    path('posts/<int:pk>/media/', views.post_media, name='post_media'),
]
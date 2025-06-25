from django.urls import path
from . import views

urlpatterns = [
     path('', views.main_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('main/', views.main_view, name='main'),
    path('upload/', views.upload_post, name='upload'),
    path('profile-upload/', views.profile_upload_view, name='profile_upload'),
    path('myprofile/', views.profile_view, name='profile_view'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/', views.profile_view_other, name='profile_view_other'),
    path('search/', views.search_users, name='search_users'),
     path('<str:username>/followers/', views.followers_list_view, name='followers_list'),
    path('<str:username>/following/', views.following_list_view, name='following_list'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat_view, name='chat_view'),


]

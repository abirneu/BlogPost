from django.urls import path, include
from . import views 
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('',views.home_page, name = 'home_page'),
    path('about/', views.about_page, name='about'),
    path('blog',views.post_list, name = 'post_list'),
    path('post/<int:id>/',views.post_details, name = 'post_details'),
    path('post/<int:id>/like',views.like_post, name = 'like_post'),
    path('post/create',views.post_create, name = 'post_create'),
    path('post/update/<int:id>/',views.post_update, name = 'post_update'),
    path('post/delete/<int:id>/',views.post_delete, name = 'post_delete'),
    path('signup/',views.signup_view, name = 'signup'),
    path('profile/',views.profile_view, name = 'profile'),
    path('login/',auth_views.LoginView.as_view(template_name='user/login.html'), name = 'login'),
    path('logout/',auth_views.LogoutView.as_view(), name = 'logout'),
    path('subscribe/youtube/', views.subscribe_youtube, name='subscribe_youtube'),
]

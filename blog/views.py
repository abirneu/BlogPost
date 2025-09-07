from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from . models import Post, Category, Tag, Comment, Profile, Subscriber
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from .forms import PostForm, CommentForm, UpdateProfileForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def about_page(request):
    """
    View function for the about page.
    """
    return render(request, 'blog/about.html')

def subscribe_youtube(request):
    """
    Handle YouTube channel subscription
    """
    if request.method == 'POST' and request.is_ajax():
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'})
        
        try:
            # Create or update subscriber
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            
            # Send confirmation email
            subject = 'Welcome to My YouTube Channel!'
            message = render_to_string('blog/email/youtube_subscription.html', {
                'email': email,
                'channel_url': 'https://www.youtube.com/@abirhasan__'  # Replace with your channel URL
            })
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=message
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for subscribing! Please check your email.'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

def post_list(request):
    categoryQ = request.GET.get('category')
    tagQ = request.GET.get('tag')
    searchQ = request.GET.get('q')

    # Get all posts with proper ordering
    posts = Post.objects.select_related('author', 'category').prefetch_related('tag').order_by('-created_at')

    # Get author search query
    authorQ = request.GET.get('author')

    # Filtering posts by category, tag, search query, and author
    if categoryQ:
        posts = posts.filter(category__name=categoryQ)

    if tagQ:
        posts = posts.filter(tag__name=tagQ)

    if authorQ:
        posts = posts.filter(
            Q(author__username__icontains=authorQ) |
            Q(author__first_name__icontains=authorQ) |
            Q(author__last_name__icontains=authorQ)
        ).distinct()

    if searchQ:
        posts = posts.filter(
            Q(title__icontains=searchQ) |
            Q(content__icontains=searchQ) |
            Q(tag__name__icontains=searchQ) |
            Q(category__name__icontains=searchQ)
        ).distinct()

    # Get all categories for the filter
    categories = Category.objects.all()

    # Pagination with 9 posts per page
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'categoryQ': categoryQ,
        'tagQ': tagQ,
        'search_query': searchQ,
        'author_query': authorQ,
    }

    # Prepare context data
    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "search_query": searchQ,
        "category_query": categoryQ,
        "tag_query": tagQ,
    }

    return render(request, 'blog/post_list.html', context)  # Always return a response
    #Category, tag, searching,pagination --> post dekhate hobe
def home_page(request):
    # Get latest posts with related data
    latest_posts = Post.objects.select_related('author', 'category').order_by('-created_at')[:3]
    
    # Get trending posts (based on view count)
    trending_posts = Post.objects.select_related('author', 'category').order_by('-view_count', '-created_at')[:4]
    
    # Get categories with post count
    categories = Category.objects.all()
    
    # Get total counts for stats
    total_posts = Post.objects.count()
    total_authors = User.objects.filter(post__isnull=False).distinct().count()
    total_comments = Comment.objects.count()
    
    context = {
        'latest_posts': latest_posts,
        'trending_posts': trending_posts,
        'categories': categories,
        'total_posts': total_posts,
        'total_authors': total_authors,
        'total_comments': total_comments,
    }
    
    return render(request, 'blog/home.html', context)

def post_details(request, id):
    post = get_object_or_404(Post,id = id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit = False) #datebase e save hobe na
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_details', id=post.id)
    
    else:
        comment_form = CommentForm()

    comments = post.comment_set.all()
    is_liked = post.liked_user.filter(id= request.user.id).exists()
    like_count = post.liked_user.count()

    context = {
        'post': post,
        'categories': Category.objects.all(),
        'tag': Tag.objects.all(),
        'comments': comments,
        'comment_form': comment_form,
        'is_liked':is_liked,
        'like_count': like_count,
    }
    post.view_count +=1
    post.save()

    return render(request, 'blog/post_details.html', context)
#post like 
@login_required
def like_post(request, id):
    post = get_object_or_404(Post, id=id)  # <-- fixed here
    if post.liked_user.filter(id=request.user.id):
        post.liked_user.remove(request.user)
    else:
        post.liked_user.add(request.user)
    return redirect('post_details', id=post.id)
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # Save tags after the post is created
            form.save_m2m()  # This saves the tags
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'blog/post_create.html', {'form': form})
@login_required
def post_update(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  # Added request.FILES
        if form.is_valid():
            form.save()
            # Save tags
            form.save_m2m()
            return redirect('post_details', id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_create.html', {'form': form})
    
@login_required
def post_delete(request,id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect('post_list')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'user/signup.html',{'form':form})
@login_required
def profile_view(request):
    section = request.GET.get('section', 'profile')
    context = {'section': section}
    
    print(f"Section: {section}")  # Debug

    if section == 'posts':
        posts = Post.objects.filter(author=request.user)
        context['posts'] = posts

    elif section == 'update':
        if request.method == 'POST':
            print("POST request received")  # Debug
            print(f"Files: {request.FILES}")  # Debug
            try:
                # Begin transaction
                from django.db import transaction
                with transaction.atomic():
                    # Create a new form instance with POST data and files
                    form = UpdateProfileForm(
                        data=request.POST,
                        files=request.FILES,
                        instance=request.user.profile
                    )
                    
                    if form.is_valid():
                        print("Form is valid")  # Debug
                        # Let the form handle all saving logic including the image
                        profile = form.save()
                        print(f"Profile image: {profile.image}")  # Debug
                        print(f"Profile image URL: {profile.image.url if profile.image else 'None'}")  # Debug
                        
                        from django.contrib import messages
                        messages.success(request, 'Your profile has been updated successfully!')
                        return redirect('profile')
                    else:
                        print("Form is invalid")  # Debug
                        print(f"Form errors: {form.errors}")  # Debug
                        from django.contrib import messages
                        messages.error(request, 'Please correct the errors below.')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating profile: {str(e)}")
                from django.contrib import messages
                messages.error(request, 'An error occurred while updating your profile.')
                print(f"Error: {str(e)}")  # Print the error for debugging
        else:
            form = UpdateProfileForm(instance=request.user.profile)
        
        # Add form to context only in the update section
        context['form'] = form

    return render(request, 'user/profile.html', context)
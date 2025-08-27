from django.shortcuts import render, get_object_or_404, redirect
from . models import Post, Category, Tag, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from .forms import PostForm, CommentForm, UpdateProfileForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def post_list(request):
    categoryQ = request.GET.get('category')
    tagQ = request.GET.get('tag')
    searchQ = request.GET.get('q')

    # Get all posts with proper ordering
    posts = Post.objects.select_related('author', 'category').prefetch_related('tag').order_by('-created_at')

    # Filtering posts by category, tag, and search query
    if categoryQ:
        posts = posts.filter(category__name=categoryQ)

    if tagQ:
        posts = posts.filter(tag__name=tagQ)

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
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'blog/post_create.html', {'form': form})
@login_required
def post_update(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = PostForm(data=request.POST, instance=post)#instance=post karon user edit e gea kichu na likhe submit dile ager j data chilo setai theke jabe
        if form.is_valid():
            form.save()
            return redirect('post_details', id =post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_create.html', {'form':form})
    
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

    if section == 'posts':
        posts = Post.objects.filter(author=request.user)
        context['posts'] = posts  # <-- use 'posts' not 'post'

    elif section == 'update':
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('/profile?section=update')
        else:
            form = UpdateProfileForm(instance=request.user)
        context['form'] = form

    return render(request, 'user/profile.html', context)
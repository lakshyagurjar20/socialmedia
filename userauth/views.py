from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Profile
from django.shortcuts import render, redirect, get_object_or_404

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user first
            Profile.objects.create(user=user)  # Auto-create empty profile
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import login_required

from .models import Post, Follow, Comment
from .forms import PostForm, CommentForm

@login_required
def main_view(request):
    followed_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=followed_users).order_by('-created_at')

    comment_forms = {post.id: CommentForm() for post in posts}
    post_comments = {
        post.id: post.comments.order_by('-created_at')[:3]  # latest 3 comments
        for post in posts
    }

    if request.method == 'POST' and 'comment_post_id' in request.POST:
        post_id = int(request.POST.get('comment_post_id'))
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post_id = post_id
            comment.user = request.user
            comment.save()
            return redirect('main')

    return render(request, 'main.html', {
        'posts': posts,
        'comment_forms': comment_forms,
        'post_comments': post_comments
    })


from .forms import PostForm
from .models import Post

@login_required
def upload_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('main')
    else:
        form = PostForm()
    return render(request, 'upload_post.html', {'form': form})


@login_required
def profile_upload_view(request):
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        profileimg = request.FILES.get('profileimg')

        profile = Profile.objects.get(user=request.user)
        profile.bio = bio
        profile.location = location
        if profileimg:
            profile.profileimg = profileimg
        profile.save()

        return redirect('main')

    return render(request, 'profile_upload.html')
from django.contrib.auth.decorators import login_required

from .models import Comment  # if not already imported

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')

    # Dict: {post.id: [comments]}
    post_comments = {post.id: Comment.objects.filter(post=post) for post in user_posts}

    liked_post_ids = request.user.post_set_liked.values_list('id', flat=True)

    followers = Follow.objects.filter(following=request.user)
    following = Follow.objects.filter(follower=request.user)

    return render(request, 'profile.html', {
        'profile': profile,
        'posts': user_posts,
        'liked_post_ids': liked_post_ids,
        'post_comments': post_comments,
        'followers_count': followers.count(),
        'following_count': following.count(),
        'followers': followers,
        'following': following,
    })


from django.shortcuts import redirect, get_object_or_404
from .models import Post
from django.contrib.auth.decorators import login_required

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)  # Dislike
    else:
        post.likes.add(user)     # Like

    return redirect('main')  # Redirect back to feed

from .models import Follow

@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect('main')  # Cannot follow yourself

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()  # Unfollow if already following
    return redirect('profile_view_other', username=username)


@login_required
def profile_view_other(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=target_user)
    user_posts = Post.objects.filter(user=target_user).order_by('-created_at')
    is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()

    followers = Follow.objects.filter(following=target_user)
    following = Follow.objects.filter(follower=target_user)

    return render(request, 'profile_other.html', {
        'profile': profile,
        'posts': user_posts,
        'target_user': target_user,
        'is_following': is_following,
        'followers_count': followers.count(),
        'following_count': following.count(),
        'followers': followers,
        'following': following,
    })

@login_required
def follow_view(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = Profile.objects.get(user=target_user)

    if request.user != target_user:
        target_profile.followers.add(request.user)

    return redirect('profile_view_user', username=username)


@login_required
def unfollow_view(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = Profile.objects.get(user=target_user)

    if request.user != target_user:
        target_profile.followers.remove(request.user)

    return redirect('profile_view_user', username=username)

from django.contrib.auth.models import User
from django.db.models import Q

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = User.objects.filter(
            Q(username__icontains=query)
        ).exclude(id=request.user.id)

    # List of users the current user is already following
    following_user_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

    return render(request, 'search.html', {
        'query': query,
        'results': results,
        'following_user_ids': following_user_ids
    })

@login_required
def followers_list_view(request, username):
    target_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=target_user)
    return render(request, 'followers_list.html', {'target_user': target_user, 'followers': followers})


@login_required
def following_list_view(request, username):
    target_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=target_user)
    return render(request, 'following_list.html', {'target_user': target_user, 'following': following})
from django.http import HttpResponseForbidden

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'edit_post.html', {'form': form, 'post': post})



@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        return redirect('main')
    
    return render(request, 'delete_post.html', {'post': post})
from .models import Post, Comment
from .forms import CommentForm
from django.contrib.auth.decorators import login_required

@login_required
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(post=post, user=request.user, text=text)
    return redirect(request.META.get('HTTP_REFERER', 'main'))


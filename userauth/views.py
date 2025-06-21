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

@login_required
def main_view(request):
    from .models import Follow  # if not already imported

    followed_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=followed_users).order_by('-created_at')

    return render(request, 'main.html', {'posts': posts})




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

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'profile': profile, 'posts': user_posts})


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

    return render(request, 'profile_other.html', {
        'profile': profile,
        'posts': user_posts,
        'target_user': target_user,
        'is_following': is_following
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

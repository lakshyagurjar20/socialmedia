from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Profile

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
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'main.html', {'posts': posts})


from .forms import PostForm
from .models import Post

@login_required
def upload_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.username
            post.save()
            return redirect('main')
    else:
        form = PostForm()
    return render(request, 'upload_post.html', {'form': form})


@login_required
def profile_upload_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profileimg = request.FILES.get('profileimg')

        if profileimg:
            profile.profileimg = profileimg

        profile.save()
        return redirect('myprofile')  # Or 'main' if that’s your homepage

    return render(request, 'profile_upload.html', {
        'profile': profile
    })

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

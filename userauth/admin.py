from django.contrib import admin
from .models import Profile, Post
from .models import Like

admin.site.register(Like)

admin.site.register(Profile)
admin.site.register(Post)


# Register your models here.

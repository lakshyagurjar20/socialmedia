from django.contrib import admin
from .models import Post, Profile

class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'caption', 'created_at']

admin.site.register(Post, PostAdmin)  # ✅ Keep this
admin.site.register(Profile)

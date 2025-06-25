from django.contrib import admin
from .models import Post, Profile, Comment, Like, Follow  # ✅ Add Comment, Like, Follow if used

class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'caption', 'created_at']

class CommentAdmin(admin.ModelAdmin):  # ✅ Comment Admin View
    list_display = ['user', 'post', 'text', 'created_at']
    search_fields = ['user__username', 'post__caption', 'text']
    list_filter = ['created_at']

admin.site.register(Post, PostAdmin)  # Already registered ✅
admin.site.register(Profile)
admin.site.register(Comment, CommentAdmin)  # ✅ Register comments cleanly
admin.site.register(Like)  # Optional, for full admin support
admin.site.register(Follow)  # Optional, for full admin support

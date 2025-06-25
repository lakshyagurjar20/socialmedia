from django.contrib import admin
from .models import Post, Profile, Comment, Like, Follow
from django.contrib.auth.models import User


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['user', 'text', 'created_at']
    readonly_fields = ['user', 'text', 'created_at']
    can_delete = False


class LikeInline(admin.TabularInline):
    model = Post.likes.through
    extra = 0
    verbose_name = "Liked By"
    verbose_name_plural = "Users who liked this post"
    readonly_fields = ['user']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'caption', 'created_at']
    inlines = [CommentInline, LikeInline]
    exclude = ['likes']


# ✅ Show followers and following as readonly fields in Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location']
    readonly_fields = ['followers_list', 'following_list']

    def followers_list(self, obj):
        followers = Follow.objects.filter(following=obj.user)
        if not followers:
            return "No followers"
        return ", ".join([f.follower.username for f in followers])
    followers_list.short_description = "Followers"

    def following_list(self, obj):
        following = Follow.objects.filter(follower=obj.user)
        if not following:
            return "Not following anyone"
        return ", ".join([f.following.username for f in following])
    following_list.short_description = "Following"


# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'post', 'text', 'created_at']
#     search_fields = ['user__username', 'text']
#     list_filter = ['created_at']


admin.site.register(Post, PostAdmin)
# admin.site.register(Follow)

from django import template

register = template.Library()

@register.filter
def is_liked_by(post, user):
    return post.like_set.filter(user=user).exists()

from django import template
from reviews.models import Comment, Post, CustomUser

register = template.Library()


@register.inclusion_tag('post_list.html')
def post_list(username):
    try:
        author = CustomUser.objects.get(user__username=username)
        post_list = Post.objects.filter(creator=author)
        return {'posts_read': post_list}
    except CustomUser.DoesNotExist:
        return None


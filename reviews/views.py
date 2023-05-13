from io import BytesIO

from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.images import ImageFile
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import SearchForm, CommentForm, PostMediaForm
from .models import Post, Comment
from .utils import average_rating
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
        return user
    except ObjectDoesNotExist:
        return None

def index(request):
    return render(request, "base.html")

def post_list(request):
    posts = Post.objects.all()
    posts_with_comments = []
    for post in posts:
        comments = post.comment_set.all()
        if comments:
            number_of_comments = len(comments)
        else:
            number_of_comments = 0
        posts_with_comments.append({"post": post, "number_of_comments": number_of_comments})

    context = {
        "post_list": posts_with_comments
    }
    return render(request, "reviews/post_list.html", context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comment_set.all()
    if comments:
        context = {
            "post": post,
            "comments": comments
        }
    else:
        context = {
            "post": post,
            "comments": None
        }
    if request.user.is_authenticated:
        max_viewed_posts_length = 10
        viewed_posts = request.session.get('viewed_posts', [])
        viewed_post = [post.id, post.title]
        if viewed_post in viewed_posts:
            viewed_posts.pop(viewed_posts.index(viewed_post))
        viewed_posts.insert(0, viewed_post)
        viewed_posts = viewed_posts[:max_viewed_posts_length]
        request.session['viewed_posts'] = viewed_posts
    return render(request, "reviews/post_detail.html", context)


def is_staff_user(user):
    return user.is_staff



@login_required
def comment_edit(request, post_pk, comment_pk=None):
    post = get_object_or_404(Post, pk=post_pk)

    if comment_pk is not None:
        comment = get_object_or_404(Comment, post_id=post_pk, pk=comment_pk)
        user = request.user
        if not user.is_staff and comment.creator.id != user.id:
            raise PermissionDenied
    else:
        comment = None

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            updated_comment = form.save(False)
            updated_comment.post = post

            if comment is None:
                messages.success(request, "Comment for \"{}\" created.".format(post))
            else:
                updated_comment.date_edited = timezone.now()
                messages.success(request, "Review for \"{}\" updated.".format(post))

            updated_comment.save()
            return redirect("post_detail", post.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, "reviews/instance-form.html",
                  {"form": form,
                   "instance": comment,
                   "model_type": "Comment",
                   "related_instance": post,
                   "related_model_type": "post"
                   })

@login_required
def post_media(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostMediaForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save(False)

            cover = form.cleaned_data.get("cover")

            if cover:
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = ImageFile(image_data)
                post.cover.save(cover.name, image_file)
            post.save()
            messages.success(request, "post \"{}\" was successfully updated.".format(post))
            return redirect("post_detail", post.pk)
    else:
        form = PostMediaForm(instance=post)

    return render(request, "reviews/instance-form.html",
                  {"instance": post, "form": form, "model_type": "post", "is_file_upload": True})
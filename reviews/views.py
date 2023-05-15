from io import BytesIO

from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.images import ImageFile
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import SearchForm, CommentForm, PostMediaForm, SettingsForm, PostForm

from .models import Post, Comment, Tag, CustomUser
from .utils import average_rating
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse


def like_unlike_post(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)
        user = request.user
        liked = False

        if user.is_authenticated:
            if user in post.likes.all():
                post.likes.remove(user)
                liked = False
            else:
                post.likes.add(user)
                liked = True

                # Create a Like instance and save it
                like = Like(user=user, post=post)
                like.save()

        return JsonResponse({"liked": liked, "likes_count": post.likes.count()})
    else:
        return JsonResponse({}, status=400)


def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
        return user
    except ObjectDoesNotExist:
        return None

def index(request):
    return render(request, "base.html")

def welcome(request):
    return render(request, 'reviews/welcome.html')

def settings_view(request):
    form = SettingsForm()

    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if form.is_valid():
            # Process form data and update user's information
            # Example: Update the user's username
            request.user.username = form.cleaned_data['username']
            request.user.save()
            return redirect('settings')

    return render(request, 'reviews/settings.html', {'form': form})

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
        "post_list": posts_with_comments,
        "is_superuser": request.user.is_superuser  # Add this line to pass the is_superuser flag to the template
    }
    return render(request, "reviews/post_list.html", context)





def profile_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            posts = Post.objects.filter(creator=request.user)
        else:
            posts = request.user.customuser.post_set.all()

        context = {
            'user': request.user,
            'posts': posts,
        }

        return render(request, 'reviews/after_log_profile.html', context)
    else:
        return render(request, 'reviews/before_logged_on.html')




def signing(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Create the superuser
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            error_message = 'Such username exists, write another one'
            return render(request, 'reviews/signup.html', {'error_message': error_message})

        user = User.objects.create_superuser(username=username, email=email, password=password)



        # Create the associated CustomUser
        custom_user = CustomUser.objects.create(user=user)

        return redirect('signup_success')  # Redirect to a success page after creating the superuser and CustomUser
    return render(request, 'reviews/signup.html')

def signup_success(request):
    return render(request, 'reviews/signup_succes.html')

User = get_user_model()

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.publication_date = timezone.now()
            post.numOfLikes = 0

            # Automatically set the creator as the current user
            post.creator = request.user

            # Automatically set the publisher as the superuser
            if request.user.is_superuser:
                post.publisher = request.user

            post.save()
            form.save_m2m()
            return redirect('profile')
    else:
        form = PostForm()

    return render(request, 'reviews/add_posts.html', {'form': form})

@login_required
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

    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        content = request.POST['content']
        creator = request.user  # Assign the authenticated user as the comment creator
        comment = Comment.objects.create(content=content, creator=creator, post=post)

        return redirect('post_detail', pk=pk)

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
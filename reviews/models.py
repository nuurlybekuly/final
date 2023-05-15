from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# class Like(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f"{self.user.username} likes {self.post.title}"
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_photos', default='static/default_avatar.jpg')

    # Add any additional fields or methods as needed

    def str(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    """A published post."""
    title = models.CharField(max_length=70,
                             help_text="The title of the post.")
    text=models.TextField()
    publication_date = models.DateField(
        verbose_name="Date the post was published.",
        null=True,
        blank=True
    )

    isbn = models.CharField(max_length=20,
                            verbose_name="ISBN number of the post.")
    numOfLikes=models.IntegerField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    cover = models.ImageField(null=True,
                              blank=True,
                              upload_to="post_covers/")
    sample = models.FileField(null=True,
                              blank=True,
                              upload_to="post_samples/")
    tags=models.ManyToManyField(Tag)
    def __str__(self):
        return "{} ({})".format(self.title, self.isbn)

    def isbn13(self):
        """ '9780316769174' => '978-0-31-676917-4' """
        return "{}-{}-{}-{}-{}".format(self.isbn[0:3], self.isbn[3:4],
                                       self.isbn[4:6], self.isbn[6:12],
                                       self.isbn[12:13])

class Comment(models.Model):
    content = models.TextField(help_text="")
    date_created = models.DateTimeField(auto_now_add=True,
                                        help_text="The date and time the review was created.")
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             help_text="The post that this review is for.")
    def __str__(self):
        return "{} - {}".format(self.creator.username, self.post.title)
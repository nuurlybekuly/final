from django.contrib import admin

from .models import Post, Comment,Tag
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomUser

class postAdmin(admin.ModelAdmin):
  model = Post
  list_display = ('title', 'isbn','publication_date')

class CustomUserInline(admin.StackedInline):
    model = CustomUser
    can_delete = False
    verbose_name_plural = 'Profile'


# Extend the UserAdmin and include the CustomUserInline
class CustomUserAdmin(UserAdmin):
  inlines = (CustomUserInline,)


# Unregister the default User admin
admin.site.unregister(User)

# Register the User model with the CustomUserAdmin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Post, postAdmin)
admin.site.register(Comment)
admin.site.register(Tag)
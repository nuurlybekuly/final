from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from reviews.models import CustomUser
def gotologin(request):
    return render(request,"base.html")

@login_required
def profile(request,username):
    user=get_object_or_404(User,username=username)
    return render(request, 'profile.html',{'user':user})

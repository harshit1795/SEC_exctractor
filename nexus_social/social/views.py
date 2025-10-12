from django.shortcuts import render
from django.contrib.auth.models import User

def user_list(request):
    users = User.objects.all()
    return render(request, 'social/user_list.html', {'users': users})
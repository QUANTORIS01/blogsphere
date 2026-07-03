from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import *


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            context = {
                'user': user
            }
            return render(request, 'registration/register_done.html', context)
    else:
        form = UserRegisterForm()
    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


def log_out(request):
    logout(request)
    return redirect('blog:index')

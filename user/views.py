from django.shortcuts import render

def sign_up(request):
    return render(request, 'registration/signup.html')

def sign_in(request):
    return render(request, 'registration/signin.html')
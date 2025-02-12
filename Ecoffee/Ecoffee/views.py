from django.shortcuts import render

def home(request):
    return render(request,'homepage.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

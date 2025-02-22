import os
from random import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from Ecoffee import settings


def home(request):
    return render(request, 'homepage.html')


def dashboard_view(request):
    return render(request, 'dashboard.html')

def welcome(response):
    return render(response, 'welcome.html')


def get_banner_images(request):
    images_folder = os.path.join(settings.STATIC_URL, 'banner_images')
    if not os.path.exists(images_folder):
        return JsonResponse({'images': []})

    images = [
        f"{settings.STATIC_URL}banner_images/{img}"
        for img in os.listdir(images_folder)
        if img.endswith(('.jpg', '.jpeg', '.png', '.gif'))
    ]

    random.shuffle(images)
    return JsonResponse({'images': images})

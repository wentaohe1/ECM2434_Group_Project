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
    images_folder = os.path.join(settings.MEDIA_ROOT, 'banner_images')
    if not os.path.exists(images_folder):
        return JsonResponse({'images': []})  # Return empty list if folder doesn't exist

    images = [
        f"{settings.MEDIA_URL}banner_images/{img}"
        for img in os.listdir(images_folder)
        if img.endswith(('.jpg', '.jpeg', '.png', '.gif'))
    ]

    random.shuffle(images)  # Optional: Randomize the order of images
    return JsonResponse({'images': images})

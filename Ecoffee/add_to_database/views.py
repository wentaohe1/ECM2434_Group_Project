from django.shortcuts import render, redirect
from EcoffeeBase.models import *
from .form import *
from django.http import HttpResponseForbidden

def shop_user_required(view_func):
    def _wrapped_view(request,*args,**kwargs):
        if not ShopUser.objects.filter(user=request.user):
            return HttpResponseForbidden("Only shop owners can access this page.")
        return view_func(request,*args,**kwargs)
    return _wrapped_view


@shop_user_required
def add_new_data(request):
    if request.method == 'POST':
        shop_form = ShopForm()
        badge_form = BadgeForm()
        # Two forms on the page, need to check which one has data

        if 'shop_form_submit' in request.POST:
            shop_form = ShopForm(request.POST)
            if shop_form.is_valid():
                active_code = shop_form.cleaned_data['active_code']
                shop=ShopUser.objects.get(user=request.user).shop_id
                shop.active_code=active_code
                shop.save()
                # redirect to home if the form is valid
                return redirect('home')
            else:
                context = {
                    'shop_form': shop_form,
                    'badge_form': badge_form
                }
                # stay on page if the form is invalid
                return render(request, 'add_new_data.html', context)
        elif 'badge_form_submit' in request.POST:
            badge_form = BadgeForm(request.POST)
            if badge_form.is_valid():
                badge_form.save()
                return redirect('home')
            else:
                context = {
                    'shop_form': shop_form,
                    'badge_form': badge_form
                }
                return render(request, 'add_new_data.html', context)
    else:
        context = {'badge_form': BadgeForm(), 'shop_form': ShopForm()}
        return render(request, 'add_new_data.html', context)

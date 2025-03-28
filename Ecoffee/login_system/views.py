from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm
from EcoffeeBase.models import *
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from .forms import PasswordResetConfirmForm
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


def login_user(request):
    if request.user.is_authenticated:  # if the user is already authenticated, redirect them to the home page
        return redirect('home')

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            current_user = CustomUser.objects.get(user=user)
            if not current_user.is_email_verified:
                messages.error(request, 'Please verify your email')
                return render(request, 'authenticate/login.html', {})

            login(request, user)
            current_user.last_active_date_time = now()
            current_user.save()
            # Redirect to the home page after successful login
            return redirect('home')
        else:
            # Error if login failed.
            messages.error(
                request, "Invalid username or password. Please try again.")
            return render(request, 'authenticate/login.html', {})

    response = render(request, 'authenticate/login.html', {})
    # Prevent caching of login page, prevents bugs.
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def logout_user(request):
    logout(request)
    messages.success(request, ("Logout successful"))
    return redirect('login')


def password_reset(request):
    if request.method == "GET":
        username = request.GET.get("username")

        if username:
            try:
                user = User.objects.get(username=username)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_complete', kwargs={
                            'uidb64': uid, 'token': token})
                )
                send_mail(
                    subject="Ecoffee Password Reset Request",
                    message=f"Click the link below to reset your password:\n{reset_link}",
                    from_email="ecoffeepta@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return redirect('password_reset_confirm')
            except User.DoesNotExist:
                return render(request, 'authenticate/password_reset.html', {'error': "User not found."})
    return render(request, 'authenticate/password_reset.html')


def password_reset_done(request):
    return render(request, 'authenticate/password_reset_done.html')


def password_reset_confirm(request):
    return render(request, 'authenticate/password_reset_confirm.html')


def password_reset_complete(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (ValueError, TypeError, User.DoesNotExist):
        user = None
    # sends a token to generate a unique id to reset the email.
    form = PasswordResetConfirmForm(initial={'uidb64': uid, 'token': token})
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():  # will only save if a valid password is input.
                user.set_password(form.cleaned_data["new_password1"])
                user.save()
                return redirect('password_reset_done')
        else:
            form = PasswordResetConfirmForm()

    return render(request, 'authenticate/password_reset_complete.html', {'form': form})


def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            new_user = CustomUser.objects.get(user=user)
            send_verification_email(user, new_user, request)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(
                    request, "Registration successful. Please check your email to verify your account.")
                return redirect('home')
            else:
                messages.error(
                    request, "Authentication failed. Please try again.")
                return redirect('register')

    else:
        form = UserRegistrationForm()

    return render(request, 'authenticate/register_user.html', {'form': form})


class custom_password_reset_confirm_view(PasswordResetConfirmView):
    template_name = "authenticate/password_reset_confirm.html"

    def form_valid(self, form):
        password1 = form.cleaned_data.get("new_password1")
        password2 = form.cleaned_data.get("new_password2")

        if password1 != password2:
            return self.render_to_response(
                self.get_context_data(
                    form=form, error="Passwords do not match!")
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("password_reset_complete")


def send_verification_email(user, custom_user, request):
    token = get_random_string(length=32)
    custom_user.email_verification_token = token  # sets a token in models
    custom_user.save()
    current_site = get_current_site(request)
    # generates verification link
    verification_link = f"{current_site.domain}{reverse('verify_email', args=[token])}"

    send_mail(
        'Verify Your Email',
        f'Please click the link to verify your email: {verification_link}',
        'ecoffeepta@gmail.com',
        [user.email],
        fail_silently=False,
    )


def verify_email(request, token):
    try:
        user = CustomUser.objects.get(
            email_verification_token=token)  # token in email link
        user.is_email_verified = True
        # confirms the email is verified and changes the verfication token to an empty string.
        user.email_verification_token = ''
        user.save()
        messages.success(request, "Email Verified, You can now login")
        return redirect('login')
    except CustomUser.DoesNotExist:
        messages.error(
            request, "Invalid verification link, please contact support")
        return redirect('home')

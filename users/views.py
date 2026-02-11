from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegisterForm, UserProfilePictureForm
from .models import UserProfilePicture
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        files = request.FILES.getlist('additional_images')  # for multiple images
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Save additional pictures
            for f in files:
                UserProfilePicture.objects.create(user=user, image=f)

            return redirect("nmdashboard:dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})




class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        return reverse_lazy("nmdashboard:dashboard")






class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)







@login_required
def upload_pictures(request):
    if request.method == "POST":
        form = UserProfilePictureForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')
        if form.is_valid() or files:
            for f in files:
                UserProfilePicture.objects.create(user=request.user, image=f)
            return redirect('users:profile')
    else:
        form = UserProfilePictureForm()
    return render(request, 'users/upload_pictures.html', {'form': form})




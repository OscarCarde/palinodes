from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, reverse
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.db import IntegrityError

from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User, Profile, Directory, User
from .forms import RepositoryForm, ProfileForm

#################__LANDING__########################

def index(request):
    return HttpResponseRedirect('dashboard')

@login_required
def dashboard(request):
    if request.method == 'POST':
        try:
            print("WOLF FENCING: performing post method")
            profile = request.user.profile
            avatar = request.FILES.get("avatar")
            print("WOLF FENCING: checking file: \n" + str(request.FILES.keys()))
            description = request.POST.get("description")
            print("WOLF FENCING: checking description: \n" + description)
            if avatar:
                profile.avatar = avatar
            if description:
                profile.description = description

            profile.save() 
            
            return HttpResponseRedirect(reverse("dashboard"))
        except Exception as e:
            print(str(e))
    return render(request, "palinodes_app/dashboard.html", {
        "profile_form": ProfileForm(), "repository_form": RepositoryForm()
    })

''' UNUSED
class CreateRepository(LoginRequiredMixin, CreateView):
    model = Directory
    form_class = RepositoryForm
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Use reverse to generate the URL using the model's id
        return reverse("repository", args=[str(self.object.id)])

@login_required
def repository_settings(request, repositorypk):

    repository = Directory.objects.get(pk=repositorypk)

    allowed = request.user in repository.collaborators.all() or request.user == repository.owner

    if allowed:
        if request.method == 'POST':
            form = RepositoryForm(request.POST)
            if form.is_valid():
                try:
                    name = form.cleaned_data.get("name")
                    description = form.cleaned_data.get("description")

                    repository.name = name
                    repository.description = description

                    # Clear existing collaborators and add the selected ones

                    repository.save()

                except Exception as e:
                    print(e)

        return render(request, "palinodes_app/settings.html", {
            "form": RepositoryForm, "repository": repository
        })
    else:
        return HttpResponseRedirect(reverse("dashboard"))
'''
@login_required
def repository_view(request, repository_id):
    repository = Directory.objects.get(id=repository_id)

    #TODO refactor to avoid unnecessary exhaustive searches
    notifications = repository.notifications.all()
    for notification in notifications:
        if request.user in notification.recipients.all():
            notification.recipients.remove(request.user)
        if not notification.recipients.exists():
            notification.delete()

    

    return render(request, "palinodes_app/repository.html", {
        "repository": repository,
        })


##################__AUTHENTICATION__################
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "palinodes_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "palinodes_app/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "palinodes_app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "palinodes_app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "palinodes_app/register.html")

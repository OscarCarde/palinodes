from django.forms import ModelForm
from .models import Directory, Profile

class RepositoryForm(ModelForm):
    
    class Meta:
        model = Directory
        fields = ["name", "description", "collaborators"]

    
class ProfileForm(ModelForm):
    class Meta:
        model= Profile
        fields = ['description', 'avatar']
import os
from typing import Iterable, Optional

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

from datetime import datetime

###__helpers__###
def get_avatar_path(instance, filename):
    return f"{instance.user.id}/{filename}"

def get_file_upload_path(instance, filename):
    return f"{instance.parent.path}/{filename}"
##################

class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    description = models.TextField(default="", max_length=300, blank=True)
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True)
        
    @property
    def all_repositories(self):
        directories = set(self.user.directories.filter(parent = None)) | set(self.user.collaborating.filter(parent = None))
        sorted_directories = sorted(directories, key=lambda directory: directory.last_edited, reverse=True)
        return sorted_directories

    @cached_property
    def repositories(self):
        directories = self.user.directories.filter(parent = None)
        sorted_directories = sorted(directories, key=lambda directory: directory.last_edited, reverse=True)
        return sorted_directories
    
    @cached_property
    def collaborating_repositories(self):
        directories = self.user.collaborating.filter(parent = None)
        sorted_directories = sorted(directories, key=lambda directory: directory.last_edited, reverse=True)
        return sorted_directories

    def __str__(self):
        return self.user.username
    
####### Hierarchical directory structure ########

class Directory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="directories")
    collaborators = models.ManyToManyField(User, blank=True, related_name="collaborating")
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="subdirectories")

    @property
    def latest_notification(self):
        if self.is_repository:
            return self.notifications.latest('timestamp')

    @property
    def repository(self):
        if self.is_repository:
            return self
        else:
            return self.parent.repository

    @property
    def number_of_collaborators(self):
        return self.collaborators.count()
    
    @property
    def path(self) -> str:
        '''recursively retreives the path of the instance directory'''
        if not self.parent:
            return f"{self.owner.id}/{self.name}"
        else:
            return f"{self.parent.path}/{self.name}"
        
    @property
    def is_repository(self):
        return self.parent == None
    
    @property
    def last_edited(self)-> datetime:
        #use recursion to find the latest child edited
        latests = []
        if self.files.exists():
            last_file_timestamp = self.files.latest("uploaded")
            latests = latests + [last_file_timestamp.uploaded]

        if self.comments.exists():
            last_comment_timestamp = self.comments.latest("timestamp")
            latests = latests + [last_comment_timestamp.timestamp]

        #BASE CASE: no subdirectories, return the date of the most recent file or comment
        if not self.subdirectories.exists() and len(latests) > 0:
             return max(latests)
        
        for subdirectory in self.subdirectories.all():
            latests.append(subdirectory.last_edited)
            
        return max(latests, default=self.created)
    
    def __str__(self):
        return f"REPOSITORY: {self.name}" if self.is_repository else self.name


class FileModel(models.Model):
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=get_file_upload_path)
    uploaded = models.DateTimeField(auto_now_add=True)

    
    @property
    def filename(self):
        return os.path.basename(self.file.name)
    
    @property
    def is_audiofile(self):
        extension3 = self.filename[-3:]
        extension4 = self.filename[-4:]
        return extension3 in ["mp3", "wav", "aac", "m4a", 'aif'] or extension4 in ["flac", "aiff"]

    def __str__(self):
        return self.filename
    
    def delete(self, *args, **kwargs):
        """
        Deletes the associated file and then the model instance.
        """
        if self.file:
            self.file.delete()
        super(FileModel, self).delete(*args, **kwargs)
###############################################

class Comment(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now_add=True)
    repository = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()

    @property
    def posted_since(self):
        #return timesince(self.timestamp, timezone.now()) + " ago"
        return f"{self.timestamp.strftime('%d-%m-%Y')} {self.timestamp.strftime('%H:%M')}"
    
    def __str__(self):
        return f"{self.user.username} commented on {self.repository.name}, {self.posted_since}"

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "sent_notifications")
    repository = models.ForeignKey(Directory, on_delete= models.CASCADE, related_name = "notifications")
    message = models.CharField(max_length=100)
    recipients = models.ManyToManyField(User, blank=True, related_name="notifications")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message + f" on {self.timestamp}"
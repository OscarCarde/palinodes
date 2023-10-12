from rest_framework import serializers
from .models import Directory, FileModel, Comment, Notification, User
import re

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        else:
            return None

    class Meta:
        model=User
        fields=['pk', 'username', 'avatar']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model= Notification
        fields=["repository", "message", "timestamp"]

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    when = serializers.SerializerMethodField()

    def get_when(self, obj):
        return obj.posted_since

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model= Comment
        fields = ['username', 'comment', 'when']

class RepositorySerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    collaborators_names = serializers.SerializerMethodField()

    def get_collaborators_names(self, obj):
        return list(obj.collaborators.values_list("username", flat=True))

    class Meta:
        model = Directory
        fields = ['name', 'description', 'created', 'owner', 'collaborators_names']
        
class DirectorySerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    def get_path(self, obj):
        #returns the directory's path minus the user id
        return re.sub("\d+/", "", obj.path, count=1)

    class Meta:
        model=Directory
        fields=['pk', 'name', 'path']

class FileSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    fileurl = serializers.SerializerMethodField()
    is_audiofile = serializers.SerializerMethodField()

    def get_is_audiofile(self, obj):
        return obj.is_audiofile
    
    def get_filename(self, obj):
        return obj.filename
    
    def get_fileurl(self, obj):
        return obj.file.url
    
    class Meta:
        model=FileModel
        fields = ['pk', 'filename', 'fileurl', 'is_audiofile']

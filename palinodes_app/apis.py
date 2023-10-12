from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

import json

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.db.models import Q

from .helpers import send_notifications

from .models import Directory, User, FileModel, Comment
from .serializers import CommentSerializer, NotificationSerializer, DirectorySerializer, FileSerializer, UserSerializer

class LeaveRepository(APIView):

    def post(self, request, repositorypk):
        try:
            repository = Directory.objects.get(pk=repositorypk)
            repository.collaborators.remove(request.user)
            return Response({"meassage": "user left repository"}, status=200)
        except Exception as e: 
            return Response({"message": str(e)}, status=500)

class AddCollaborator(APIView):

    def post(self, request):
        try:
            new_collaboratorpk = request.data["newCollaboratorpk"]
            repositorypk = request.data["repositorypk"]

            repository = Directory.objects.get(pk=repositorypk)
            new_collaborator = User.objects.get(pk=new_collaboratorpk)

            if new_collaborator != repository.owner:

                if repository.owner == request.user or repository.collaborators.contains(request.user):
                    repository.collaborators.add(new_collaborator)

                    return Response({"message": "user added successfully"}, status=200)
                else:
                    return Response({"message": "You don't have permission to do this"}, status=500)
            else:
                return Response({"message": "user already owns the repository"}, status=500)
    
        except Exception as e:
            return Response({"message": str(e)}, status=500)

class SearchCollaborators(APIView):

    def get(self, request):
        substring = request.query_params.get("substring", "")
        try:
            matched = User.objects.filter(Q(username__startswith=substring))

            serializer = UserSerializer(matched, many=True)

            return Response({"message":"request successful", "users": serializer.data}, status=200)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

class RemoveCollaborator(APIView):

    def post(self, request, repositorypk):
        collaboratorpk = request.data["pk"]

        try:
            repository = Directory.objects.get(pk= repositorypk)
            collaborator = User.objects.get(pk=collaboratorpk)

            if request.user == repository.owner:
                repository.collaborators.remove(collaborator)
                return Response({"message": f"{collaborator.username} removed successfully"}, status=200)
            else:
                return Response({"message": "You don't have permission to do this"}, status=403)
        except Directory.DoesNotExist:
            return Response({"message": f"repository with id {repositorypk} can't be found."}, status=400)
        except User.DoesNotExist: 
            return Response({"message": f"user with id {collaboratorpk} can't be found"}, status=401)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

class NotificationsList(APIView):

    def get(self, request):
        notifications = request.user.notifications.all()
        data = NotificationSerializer(notifications, many=True).data
        return Response(data)

class DirectoryContents(APIView):

    def get(self, request):
        pk = request.query_params.get("pk", -1)
        try:
            directory = Directory.objects.get(pk=pk)
            directory_serializer = DirectorySerializer(directory)
            
            subdirectories = directory.subdirectories
            subdirectories_serializer = DirectorySerializer(subdirectories, many=True)

            files = directory.files
            file_serializer = FileSerializer(files, many=True)

            #add the parent directory if there is one, otherwise, set the parent field to null
            parent = directory.parent
            parent_serializer = DirectorySerializer(parent) if parent else None
            parent_data = parent_serializer.data if parent_serializer else None

            return Response({"message": "directory contents retreived successfully", "parent": parent_data, "current": directory_serializer.data, "subdirectories":subdirectories_serializer.data, "files": file_serializer.data}, status=200)

        except Directory.DoesNotExist:
            return Response({"message": f"directory with id {pk} does not exist"}, status=400)
        except FileModel.DoesNotExist:
            return Response({"message": f"file with id {pk} does not exist"}, status=400)
        except Exception as e:
            return Response({"message": str(e)}, status=500)
    
class NewDirectory(APIView):

    def post(self, request):
        #get name and parent pk
        name = request.data["name"]
        parent_pk = request.data["parent_pk"]

        try:
            #create new directory with parent
            parent= Directory.objects.get(pk=parent_pk)
            new_directory = Directory.objects.create(name= name, parent= parent, owner= parent.owner)
            new_directory.collaborators.set(parent.collaborators.all())
            new_directory.save()

            send_notifications(request.user, new_directory.repository, f"Directory {name} added by {request.user.username}")
            

            return Response({"message": "directory created successfully", "directory_pk": new_directory.pk}, status=200)
        except Directory.DoesNotExist:
            return Response({"message": f"directory with primary key {parent_pk} does not exist"}, status=400)
        except Exception as e:
            return Response({"message":f"{str(e)} \n user: {request.user.username}"}, status=500)
        
class DeleteDirectory(APIView):

    def post(self, request):
        directorypk = request.data["directorypk"]

        try:
            directory = Directory.objects.get(pk=directorypk)
            
            if not directory.is_repository:
                send_notifications(request.user, directory.repository, f"Directory  {directory.name} was deleted with its contents by {request.user.username}")

            directory.delete()

            return Response({"message": "directory deleted successfully"}, status=200)
        except Directory.DoesNotExist:
            return Response({"message": f"primary key {directorypk} doesn't match any existing directory"}, status=400)
        except Exception as e:
            return Response({"message": f"delete api got Error:\n{str(e)}"}, status=500)

class DeleteFile(APIView):

    def post(self, request):
        filepk = request.data["filepk"]

        try:
            file = FileModel.objects.get(pk=filepk)

            send_notifications(request.user, file.parent.repository, f"File {file.filename} was deleted by {request.user.username}") 

            file.delete()
            return Response({"message": "file deleted successfully"}, status=200)
        except FileModel.DoesNotExist:
            return Response({"message": f"primary key {filepk} doesn't match any existing directory"}, status=400)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

class UploadFile(APIView):
    parsere_classes = (MultiPartParser,)
    def post(self, request):
        try:
            file = request.data['file']
            parentpk = request.data['parentpk']

            parent = Directory.objects.get(pk=int(parentpk))
        
            file_instance = FileModel.objects.create(parent=parent, file=file)
            file_instance.save()

            send_notifications(request.user, file_instance.parent.repository, f"File {file_instance.filename} added by {request.user.username}")

            return Response({'message': 'File uploaded sucessfully'}, status=200)
        except Directory.DoesNotExist:
            return Response({'message': f'Parent directory with PRIMARY KEY: {parentpk} not found'}, status=400)
        except Exception as e:
            return Response({'message': str(e)}, status=500)

class NewComment(APIView):

    def post(self, request):
        try:
            #retreive repository
            repositorypk = request.data["repositorypk"]
            repository = Directory.objects.get(pk=int(repositorypk))

            #create comment
            message = request.data["comment"]
            comment_instance = Comment.objects.create(comment=message, repository=repository, user=request.user)
            comment_instance.save()

            send_notifications(request.user, repository, f"{request.user.username} commented")

            return Response({'message': "comment saved successfully"}, status=200)
        except Directory.DoesNotExist:
            return Response({'message': f'directory with PRIMARY KEY: {repositorypk} not found'}, status=400)
        except Exception as e:
            return Response({'message': str(e)}, status=500)

class Comments(APIView):

    def get(self, request):
        repositorypk = request.query_params.get("pk", -1)
        repository = Directory.objects.get(pk=repositorypk)

        comments = repository.comments.order_by("-timestamp")
        comments_serializer = CommentSerializer(comments, many=True)

        return Response({"comments": comments_serializer.data})

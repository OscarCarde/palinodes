from django.urls import path
from . import views
from . import apis

urlpatterns = [
    path('', views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("repository/<int:repository_id>", views.repository_view, name="repository"),
    #API urls
    path("api/leave/<int:repositorypk>", apis.LeaveRepository.as_view(), name = "leave"),
    path("api/add-collaborator", apis.AddCollaborator.as_view(), name="add-collaborator"),
    path("api/search-collaborators", apis.SearchCollaborators.as_view(), name="search-collaborator"),
    path("api/notifications", apis.NotificationsList.as_view(), name="notifications"),
    path("api/directory", apis.DirectoryContents.as_view(), name="directory"),
    path("api/comments", apis.Comments.as_view(), name="comments"),
    path("api/new-directory", apis.NewDirectory.as_view(), name="new-directory"),
    path("api/new-file", apis.UploadFile.as_view(), name="new-file"),
    path("api/new-comment", apis.NewComment.as_view(), name="new-comment"),
    path("api/delete-directory", apis.DeleteDirectory.as_view(), name="delete-directory"),
    path("api/delete-file", apis.DeleteFile.as_view(), name="delete-file"),
    path("api/remove-collaborator/<int:repositorypk>", apis.RemoveCollaborator.as_view(), name="remove_collaborator"),
    #Login urls
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout")
]

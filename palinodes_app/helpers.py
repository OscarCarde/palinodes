from .models import User, Directory, Notification

def send_notifications(sender: User, repository: Directory, message: str) -> None:
    recipients = (set(repository.collaborators.all()) | {repository.owner}) - {sender}
    if len(recipients) > 0:
        notification = Notification.objects.create(sender=sender, repository=repository, message=message)
        notification.save()
        notification.recipients.set(recipients)
        notification.save()
   

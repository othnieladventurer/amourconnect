from django.db import models
from users.models import User

# Create your models here.
class Like(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_sent")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_received")
    created_at = models.DateTimeField(auto_now_add=True)
    is_matched = models.BooleanField(default=False)  # becomes True when a match happens

    class Meta:
        unique_together = ('from_user', 'to_user')  # prevent duplicate likes

    def __str__(self):
        return f"{self.from_user.username} liked {self.to_user.username}"








class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # prevent duplicate matches

    def __str__(self):
        return f"Match: {self.user1.username} & {self.user2.username}"







class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_received")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"








class ProfileView(models.Model):
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="views_made")
    viewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="views_received")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('viewer', 'viewed')

    def __str__(self):
        return f"{self.viewer.username} viewed {self.viewed.username}"
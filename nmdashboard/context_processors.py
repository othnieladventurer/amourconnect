from .models import Message

def unread_messages(request):
    """
    Provides unread messages count and latest messages for the current user.
    """
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
        latest_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')[:5]
    else:
        unread_count = 0
        latest_messages = []

    return {
        'unread_messages_count': unread_count,
        'latest_messages': latest_messages,
    }

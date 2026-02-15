from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User, UserProfilePicture
from .forms import UserProfileForm, UserProfilePictureForm
from django.http import HttpResponseForbidden
from datetime import datetime
from .models import Like, Match
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from datetime import date
from .models import *
from django.db.models.functions import Random
from django.core.serializers.json import DjangoJSONEncoder



# Create your views here.
@login_required
def dashboard(request):
    user = request.user

    # -----------------------------
    # Likes RECEIVED
    # -----------------------------
    likes_received = (
        Like.objects
        .filter(to_user=user)
        .select_related("from_user")
        .distinct()
    )

    likes_received_json = [
        {
            "id": like.id,
            "from_user": {
                "id": like.from_user.id,
                "username": like.from_user.username,
                "profile_photo": (
                    like.from_user.profile_photo.url
                    if like.from_user.profile_photo
                    else "/static/images/default-profile.png"
                ),
                "bio": like.from_user.bio or "",
            },
        }
        for like in likes_received
    ]

    # -----------------------------
    # Matches involving current user
    # -----------------------------
    user_matches = (
        Match.objects
        .filter(Q(user1=user) | Q(user2=user))
        .select_related("user1", "user2")
        .distinct()
    )

    matched_user_ids = []
    matches = []

    for match in user_matches:
        other_user = match.user2 if match.user1 == user else match.user1

        matched_user_ids.append(other_user.id)

        matches.append({
            "other_user": {
                "id": other_user.id,
                "username": other_user.username,
                "profile_photo": (
                    other_user.profile_photo.url
                    if other_user.profile_photo
                    else "/static/images/default-profile.png"
                ),
            },
            "created_at": match.created_at,
        })

    # -----------------------------
    # Users already liked
    # -----------------------------
    liked_user_ids = (
        Like.objects
        .filter(from_user=user)
        .values_list("to_user_id", flat=True)
    )

    # -----------------------------
    # Profiles to show (RANDOMIZED)
    # -----------------------------
    profiles = (
        User.objects
        .filter(is_active=True)
        .exclude(id=user.id)
        .exclude(id__in=matched_user_ids)
        .exclude(id__in=liked_user_ids)
    )

    # Gender filtering
    if user.interested_in != "everyone":
        profiles = profiles.filter(gender=user.interested_in)

    profiles = profiles.filter(
        Q(interested_in=user.gender) | Q(interested_in="everyone")
    )

    # 🔥 RANDOM ORDER EVERY PAGE LOAD
    profiles = profiles.order_by(Random())

    profiles_json = [
        {
            "id": p.id,
            "username": p.username,
            "bio": p.bio or "",
            "birth_date": (p.birth_date.isoformat() if p.birth_date else None),
            "gender": p.gender or "",
            "interested_in": p.interested_in or "",
            "location": p.location or "",
            "profile_photo": p.profile_photo.url if p.profile_photo else "/static/images/default-profile.png",
            "career": p.career or "",
            "education": p.education or "",
            "passions": p.passions or "",
            "hobbies": p.hobbies or "",
            "height": p.height or None,
            "favorite_music": p.favorite_music or "",
            "is_verified": p.is_verified,
        }
        for p in profiles
    ]


    context = {
        "profiles_json": json.dumps(profiles_json, cls=DjangoJSONEncoder),
        "likes_received": json.dumps(likes_received_json, cls=DjangoJSONEncoder),
        "matches": matches,
        "is_paid": getattr(user, "is_paid", False),
    }

    return render(request, "nmdashboard/dashboard.html", context)






@login_required
@require_POST
def like_or_pass(request):
    action = request.POST.get("action")  # "like" or "pass"
    to_user_id = request.POST.get("user_id")

    if not to_user_id:
        return JsonResponse({"error": "Invalid user"}, status=400)

    from_user = request.user

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # ----------------
    # PASS = TEMPORARY, DO NOT SAVE
    # ----------------
    if action == "pass":
        return JsonResponse({"status": "passed", "is_match": False})

    # ----------------
    # LIKE
    # ----------------
    like, created = Like.objects.get_or_create(
        from_user=from_user,
        to_user=to_user,
    )

    # Check for reciprocal like
    reciprocal_like = Like.objects.filter(
        from_user=to_user,
        to_user=from_user
    ).first()

    if reciprocal_like:
        # MATCH
        like.is_matched = True
        reciprocal_like.is_matched = True
        like.save()
        reciprocal_like.save()

        # Create match entry
        user1, user2 = sorted([from_user, to_user], key=lambda u: u.id)
        match, _ = Match.objects.get_or_create(user1=user1, user2=user2)

        matched_user_info = {
            "id": to_user.id,
            "username": to_user.username,
            "profile_photo": to_user.profile_photo.url if to_user.profile_photo else "/static/images/default-profile.png",
        }

        return JsonResponse({
            "status": "matched",
            "is_match": True,
            "matched_user": matched_user_info
        })

    return JsonResponse({"status": "liked", "is_match": False})



@login_required
def voir_profil(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Compute age
    age = None
    if user.birth_date:
        today = date.today()
        age = today.year - user.birth_date.year
        if (today.month, today.day) < (user.birth_date.month, user.birth_date.day):
            age -= 1

    hobbies_list = [h.strip() for h in user.hobbies.split(",") if h.strip()]
    passions_list = [p.strip() for p in user.passions.split(",") if p.strip()]

    return render(request, "nmdashboard/voir_profil.html", {
        "profile_suser": user,
        "age": age,
        "hobbies_list": hobbies_list,
        "passions_list": passions_list,
    })






@login_required
def chat_view(request, user_id):
    current_user = request.user
    other_user = get_object_or_404(User, id=user_id)

    # Prevent messaging yourself
    if current_user == other_user:
        return HttpResponseForbidden("Vous ne pouvez pas vous envoyer un message à vous-même.")

    # Check if users are matched
    is_matched = Match.objects.filter(
        Q(user1=current_user, user2=other_user) |
        Q(user1=other_user, user2=current_user)
    ).exists()

    if not is_matched:
        return HttpResponseForbidden("Vous ne pouvez envoyer des messages qu'aux utilisateurs avec lesquels vous avez un match.")

    # Fetch all messages between these two users
    messages = Message.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by("timestamp")

    # Mark unread messages as read
    Message.objects.filter(sender=other_user, receiver=current_user, is_read=False).update(is_read=True)

    # Handle sending a new message
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(sender=current_user, receiver=other_user, content=content)
        return redirect("nmdashboard:chat", user_id=other_user.id)

    context = {
        "other_user": other_user,
        "messages": messages,
    }

    return render(request, "nmdashboard/chat.html", context)









@login_required
def unmatch_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        other_user = get_object_or_404(User, id=user_id)

        # Delete match
        match = Match.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).first()

        if match:
            match.delete()

            # 🔥 Remove ONLY the current user's like
            Like.objects.filter(
                from_user=request.user,
                to_user=other_user
            ).delete()

            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "error", "message": "No match found."})

    return JsonResponse({"status": "error", "message": "Invalid request."})






@login_required
def block_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        other_user = get_object_or_404(User, id=user_id)

        # Unmatch if matched
        Match.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).delete()

        # Block
        blocked, created = BlockedUser.objects.get_or_create(
            blocker=request.user,
            blocked=other_user
        )
        if created:
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Already blocked."})
    return JsonResponse({"status": "error", "message": "Invalid request."})



@login_required
def my_profile(request):
    user = request.user

    if request.method == "POST":
        # ---------- BASIC FIELDS ----------
        user.username = request.POST.get("username", "").strip()
        user.email = request.POST.get("email", "").strip()
        user.bio = request.POST.get("bio", "").strip()
        user.gender = request.POST.get("gender", "")
        user.interested_in = request.POST.get("interested_in", "")
        user.location = request.POST.get("location", "").strip()
        user.height = request.POST.get("height") or None
        user.career = request.POST.get("career", "").strip()
        user.education = request.POST.get("education", "").strip()
        user.passions = request.POST.get("passions", "").strip()
        user.hobbies = request.POST.get("hobbies", "").strip()
        user.favorite_music = request.POST.get("favorite_music", "").strip()

        # ---------- BIRTH DATE ----------
        birth_date_str = request.POST.get("birth_date", "").strip()
        if birth_date_str:
            try:
                user.birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                user.birth_date = None
        else:
            user.birth_date = None

        # ---------- PROFILE PHOTO ----------
        if request.FILES.get("profile_photo"):
            user.profile_photo = request.FILES["profile_photo"]

        user.save()

        # ---------- MULTIPLE PICTURES ----------
        files = request.FILES.getlist("pictures")  # <input name="pictures" multiple>
        existing_count = user.pictures.count()
        remaining_slots = 10 - existing_count

        for i, f in enumerate(files):
            if i >= remaining_slots:
                break
            UserProfilePicture.objects.create(user=user, image=f)

        return redirect("nmdashboard:my_profile")

    # GET request: pass existing pictures
    pictures = user.pictures.all()
    return render(request, "nmdashboard/my_profile.html", {"user": user, "pictures": pictures})







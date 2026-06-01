from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topics, Messages, Follow, TopicFollow
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RoomForm

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
            
    context = {'page': 'login'}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {'form': form, 'page': 'register'}
    return render(request, 'base/login_register.html', context)
# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        topic__name__icontains=q
    )
    topics = Topics.objects.all()
    room_count = rooms.count()
    room_messages = Messages.objects.filter(room__topic__name__icontains=q)[:5]

    followed_topic_ids = []
    if request.user.is_authenticated:
        followed_topic_ids = list(
            TopicFollow.objects.filter(user=request.user).values_list('topic_id', flat=True)
        )

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'followed_topic_ids': followed_topic_ids,
    }
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # Only top-level messages (not replies)
    room_messages = room.messages_set.filter(reply_to=None).order_by('created')

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        reply_to_id = request.POST.get('reply_to')
        if body:
            reply_to_obj = None
            if reply_to_id:
                try:
                    reply_to_obj = Messages.objects.get(id=reply_to_id, room=room)
                except Messages.DoesNotExist:
                    pass
            Messages.objects.create(
                user=request.user,
                room=room,
                body=body,
                reply_to=reply_to_obj
            )
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages}
    return render(request, 'base/room.html', context)

from django.contrib.auth.decorators import login_required
from .forms import RoomForm

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
        
    form = RoomForm(instance=room)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
            
    context = {'form': form, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
        
    if request.method == 'POST':
        room.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Messages.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
        
    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=message.room.id)
        
    return render(request, 'base/delete.html', {'obj': message})

def userProfile(request, pk):
    from django.contrib.auth.models import User
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.messages_set.all()
    topics = Topics.objects.all()
    follower_count = user.followers.count()
    is_following = False
    followed_topic_ids = []
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        followed_topic_ids = list(
            TopicFollow.objects.filter(user=request.user).values_list('topic_id', flat=True)
        )
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        'follower_count': follower_count,
        'is_following': is_following,
        'followed_topic_ids': followed_topic_ids,
    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def followUser(request, pk):
    from django.contrib.auth.models import User
    user_to_follow = User.objects.get(id=pk)
    
    if request.user == user_to_follow:
        return redirect('user-profile', pk=pk)

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    if not created:
        # Already following — unfollow
        follow_obj.delete()

    return redirect('user-profile', pk=pk)

@login_required(login_url='login')
def followTopic(request, pk):
    topic = Topics.objects.get(id=pk)
    follow_obj, created = TopicFollow.objects.get_or_create(user=request.user, topic=topic)
    if not created:
        follow_obj.delete()
    # Redirect back to where we came from
    next_url = request.GET.get('next', '/')
    return redirect(next_url)
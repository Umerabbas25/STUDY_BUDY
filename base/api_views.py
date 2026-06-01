from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Topics, Room, Messages, Follow, TopicFollow
from .serializers import (
    UserSerializer, RegisterSerializer,
    TopicSerializer, RoomSerializer,
    MessageSerializer, ReplySerializer,
    FollowSerializer, TopicFollowSerializer,
)
from .permissions import IsHostOrReadOnly, IsOwnerOrReadOnly


# ── Auth ───────────────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    """POST /api/register/ — Create a new user account."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ── Users ──────────────────────────────────────────────────────
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/users/       — list all users
    GET /api/users/<id>/  — user detail + stats
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """GET /api/users/me/ — return the current authenticated user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """GET /api/users/<id>/rooms/ — rooms hosted by this user."""
        user = self.get_object()
        rooms = Room.objects.filter(host=user)
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """GET /api/users/<id>/followers/ — list of followers."""
        user = self.get_object()
        follows = Follow.objects.filter(following=user).select_related('follower')
        data = [UserSerializer(f.follower).data for f in follows]
        return Response(data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """GET /api/users/<id>/following/ — list of users this user follows."""
        user = self.get_object()
        follows = Follow.objects.filter(follower=user).select_related('following')
        data = [UserSerializer(f.following).data for f in follows]
        return Response(data)


# ── Topics ─────────────────────────────────────────────────────
class TopicViewSet(viewsets.ModelViewSet):
    """
    GET    /api/topics/       — list all topics
    POST   /api/topics/       — create topic (auth required)
    GET    /api/topics/<id>/  — topic detail
    DELETE /api/topics/<id>/  — delete topic (auth required)
    """
    queryset = Topics.objects.all().order_by('name')
    serializer_class = TopicSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """POST/DELETE /api/topics/<id>/follow/ — follow or unfollow a topic."""
        topic = self.get_object()
        follow_obj, created = TopicFollow.objects.get_or_create(user=request.user, topic=topic)
        if not created:
            follow_obj.delete()
            return Response({'status': 'unfollowed', 'topic': topic.name})
        return Response({'status': 'followed', 'topic': topic.name}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """GET /api/topics/<id>/rooms/ — rooms under this topic."""
        topic = self.get_object()
        rooms = Room.objects.filter(topic=topic)
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data)


# ── Rooms ──────────────────────────────────────────────────────
class RoomViewSet(viewsets.ModelViewSet):
    """
    GET    /api/rooms/       — list rooms (supports ?search=, ?topic=)
    POST   /api/rooms/       — create a room (auth required)
    GET    /api/rooms/<id>/  — room detail
    PATCH  /api/rooms/<id>/  — update room (host only)
    DELETE /api/rooms/<id>/  — delete room (host only)
    """
    queryset = Room.objects.all().select_related('host', 'topic').order_by('-created')
    serializer_class = RoomSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'topic__name', 'host__username']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsHostOrReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        topic = self.request.query_params.get('topic')
        if topic:
            qs = qs.filter(topic__name__icontains=topic)
        return qs

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """GET /api/rooms/<id>/messages/ — all messages in this room (threaded)."""
        room = self.get_object()
        top_level = room.messages_set.filter(reply_to=None).order_by('created')
        serializer = MessageSerializer(top_level, many=True, context={'request': request})
        return Response(serializer.data)


# ── Messages ───────────────────────────────────────────────────
class MessageViewSet(viewsets.ModelViewSet):
    """
    GET    /api/messages/       — list messages
    POST   /api/messages/       — post a message (auth required)
    GET    /api/messages/<id>/  — message detail with replies
    DELETE /api/messages/<id>/  — delete own message
    """
    queryset = Messages.objects.all().select_related('user', 'room').order_by('created')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """GET /api/messages/<id>/replies/ — all replies to this message."""
        message = self.get_object()
        replies = message.replies.all().order_by('created')
        serializer = ReplySerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)


# ── Follow Users ───────────────────────────────────────────────
class FollowUserView(APIView):
    """
    POST   /api/users/<id>/follow/ — follow a user
    DELETE /api/users/<id>/follow/ — unfollow a user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            target = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        if target == request.user:
            return Response({'error': 'You cannot follow yourself'}, status=400)

        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )
        if not created:
            follow_obj.delete()
            return Response({
                'status': 'unfollowed',
                'user': target.username,
                'follower_count': target.followers.count()
            })
        return Response({
            'status': 'followed',
            'user': target.username,
            'follower_count': target.followers.count()
        }, status=status.HTTP_201_CREATED)


# ── Search ─────────────────────────────────────────────────────
class SearchView(APIView):
    """GET /api/search/?q=term — search rooms, topics, and users at once."""
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '')
        rooms = Room.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(topic__name__icontains=q)
        )[:5]
        topics = Topics.objects.filter(name__icontains=q)[:5]
        users = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
        )[:5]

        return Response({
            'rooms':  RoomSerializer(rooms, many=True, context={'request': request}).data,
            'topics': TopicSerializer(topics, many=True).data,
            'users':  UserSerializer(users, many=True).data,
        })

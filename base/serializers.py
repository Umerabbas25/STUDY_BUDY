from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Topics, Room, Messages, Follow, TopicFollow


# ── User ──────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    room_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'follower_count', 'following_count', 'room_count']

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_room_count(self, obj):
        return obj.room_set.count()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'].lower(),
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


# ── Topic ──────────────────────────────────────────────────────
class TopicSerializer(serializers.ModelSerializer):
    room_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = Topics
        fields = ['id', 'name', 'room_count', 'follower_count', 'created']

    def get_room_count(self, obj):
        return obj.room_set.count()

    def get_follower_count(self, obj):
        return obj.followers.count()


# ── Room ───────────────────────────────────────────────────────
class RoomSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topics.objects.all(), source='topic', write_only=True
    )
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'host', 'topic', 'topic_id',
                  'message_count', 'created', 'updated']
        read_only_fields = ['id', 'host', 'created', 'updated']

    def get_message_count(self, obj):
        return obj.messages_set.count()

    def create(self, validated_data):
        request = self.context['request']
        room = Room.objects.create(host=request.user, **validated_data)
        return room


# ── Message / Reply ────────────────────────────────────────────
class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Messages
        fields = ['id', 'user', 'body', 'created', 'updated']


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    reply_to_id = serializers.PrimaryKeyRelatedField(
        queryset=Messages.objects.all(), source='reply_to',
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Messages
        fields = ['id', 'user', 'room', 'body', 'reply_to_id',
                  'replies', 'created', 'updated']
        read_only_fields = ['id', 'user', 'replies', 'created', 'updated']

    def create(self, validated_data):
        request = self.context['request']
        msg = Messages.objects.create(user=request.user, **validated_data)
        return msg


# ── Follow ─────────────────────────────────────────────────────
class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    following_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='following', write_only=True
    )

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'following_id', 'created']
        read_only_fields = ['id', 'follower', 'created']


class TopicFollowSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topics.objects.all(), source='topic', write_only=True
    )

    class Meta:
        model = TopicFollow
        fields = ['id', 'user', 'topic', 'topic_id', 'created']
        read_only_fields = ['id', 'user', 'created']

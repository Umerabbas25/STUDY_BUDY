from django.contrib import admin
from django.utils.html import format_html
from .models import Topics, Room, Messages, Follow, TopicFollow


# ── Inline: show replies inside a message ─────────────────────
class ReplyInline(admin.TabularInline):
    model = Messages
    fk_name = 'reply_to'
    extra = 1                          # one blank row to type a new reply
    fields = ('user', 'body', 'created')
    readonly_fields = ('created',)
    verbose_name = 'Reply'
    verbose_name_plural = 'Replies'
    show_change_link = True


# ── Inline: messages inside a room ───────────────────────────
class MessageInline(admin.TabularInline):
    model = Messages
    fk_name = 'room'
    extra = 0
    fields = ('user', 'body', 'reply_to', 'created')
    readonly_fields = ('created',)
    show_change_link = True


# ── Topics ────────────────────────────────────────────────────
@admin.register(Topics)
class TopicsAdmin(admin.ModelAdmin):
    list_display  = ('name', 'room_count', 'follower_count', 'created')
    search_fields = ('name',)
    ordering      = ('name',)

    @admin.display(description='Rooms')
    def room_count(self, obj):
        return obj.room_set.count()

    @admin.display(description='Followers')
    def follower_count(self, obj):
        return obj.followers.count()


# ── Rooms ─────────────────────────────────────────────────────
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ('name', 'host', 'topic', 'message_count', 'created')
    list_filter   = ('topic',)
    search_fields = ('name', 'description', 'host__username')
    ordering      = ('-created',)
    inlines       = [MessageInline]
    readonly_fields = ('created', 'updated')
    fieldsets = (
        ('Room Info', {
            'fields': ('name', 'description', 'topic', 'host')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Messages')
    def message_count(self, obj):
        return obj.messages_set.count()


# ── Messages ──────────────────────────────────────────────────
@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display  = ('short_body', 'user', 'room', 'is_reply', 'reply_to', 'created')
    list_filter   = ('room',)
    search_fields = ('body', 'user__username', 'room__name')
    ordering      = ('-created',)
    inlines       = [ReplyInline]          # <-- host can add replies from here
    readonly_fields = ('created', 'updated')
    fieldsets = (
        ('Message', {
            'fields': ('user', 'room', 'body', 'reply_to')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Body')
    def short_body(self, obj):
        return obj.body[:60] + ('...' if len(obj.body) > 60 else '')

    @admin.display(description='Is Reply', boolean=True)
    def is_reply(self, obj):
        return obj.reply_to is not None


# ── Follow ────────────────────────────────────────────────────
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display  = ('follower', 'following', 'created')
    search_fields = ('follower__username', 'following__username')
    ordering      = ('-created',)


# ── TopicFollow ───────────────────────────────────────────────
@admin.register(TopicFollow)
class TopicFollowAdmin(admin.ModelAdmin):
    list_display  = ('user', 'topic', 'created')
    search_fields = ('user__username', 'topic__name')
    ordering      = ('-created',)


# ── Admin site branding ────────────────────────────────────────
admin.site.site_header  = 'StudyBud Admin'
admin.site.site_title   = 'StudyBud'
admin.site.index_title  = 'Welcome to StudyBud Admin Panel'
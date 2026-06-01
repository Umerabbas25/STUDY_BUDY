from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import api_views
from . import ai_views

router = DefaultRouter()
router.register(r'users',    api_views.UserViewSet,    basename='user')
router.register(r'topics',   api_views.TopicViewSet,   basename='topic')
router.register(r'rooms',    api_views.RoomViewSet,    basename='room')
router.register(r'messages', api_views.MessageViewSet, basename='message')

urlpatterns = [
    # ── Router-generated endpoints ────────────────────────────
    path('', include(router.urls)),

    # ── Auth ─────────────────────────────────────────────────
    path('register/',          api_views.RegisterView.as_view(),  name='api-register'),
    path('token/',             TokenObtainPairView.as_view(),     name='token-obtain'),
    path('token/refresh/',     TokenRefreshView.as_view(),        name='token-refresh'),
    path('token/verify/',      TokenVerifyView.as_view(),         name='token-verify'),

    # ── Follow User ───────────────────────────────────────────
    path('users/<int:pk>/follow/', api_views.FollowUserView.as_view(), name='api-follow-user'),

    # ── Global Search ─────────────────────────────────────────
    path('search/',            api_views.SearchView.as_view(),    name='api-search'),

    # ── AI Endpoints ──────────────────────────────────────────
    path('rooms/<int:pk>/summarize/', ai_views.RoomSummaryView.as_view(), name='api-ai-summarize'),
    path('messages/<int:pk>/suggest-reply/', ai_views.SmartReplyView.as_view(), name='api-ai-suggest-reply'),
    path('ai-chat/', ai_views.AIChatView.as_view(), name='api-ai-chat'),
]


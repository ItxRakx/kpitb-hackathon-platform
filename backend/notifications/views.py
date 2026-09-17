from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        unread_only = request.query_params.get("unread_only", "").lower()
        if unread_only in ("true", "1", "yes"):
            qs = qs.filter(read_at__isnull=True)
        return Response(
            NotificationSerializer(qs.order_by("-created_at"), many=True).data
        )


class MarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk=None):
        try:
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            raise NotFound("Notification not found.")
        if notification.user_id != request.user.id:
            raise PermissionDenied("Not your notification.")
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return Response(NotificationSerializer(notification).data)


class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = (
            Notification.objects.filter(user=request.user, read_at__isnull=True)
            .update(read_at=timezone.now())
        )
        return Response({"marked_read": count})


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "app": "notifications"}, status=status.HTTP_200_OK)

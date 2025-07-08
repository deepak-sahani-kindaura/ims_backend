from django.urls import path

from notification.views import NotificationViewSet


urlpatterns = [
    path(
        "notification",
        NotificationViewSet.as_view(NotificationViewSet.get_method_view_mapping()),
        name="notification",
    ),
]

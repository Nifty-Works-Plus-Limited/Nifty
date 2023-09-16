from django.urls import path, include

urlpatterns = [
    # OAuth2.0
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

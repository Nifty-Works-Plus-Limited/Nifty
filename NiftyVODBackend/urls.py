from django.contrib import admin
from django.db import router
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from content.views import create_movie_view
from django.http import JsonResponse


urlpatterns = [
    path('admin/', admin.site.urls),

    #urls
    path('api/', include('api.urls')),
    path('api/', include('rest_framework.urls')),

    #testing signed urls
    path('testSigned/', create_movie_view),
    
]

#Fallback errors
handler400 = lambda request, exception=None: JsonResponse({
          "status": "error",
          "code": 400,
          "data": None,
          "message": "Bad request"
        })

handler403 =  lambda request, exception=None: JsonResponse({
          "status": "error",
          "code": 403,
          "data": None,
          "message": "Your are not authorized to access this resource"
        })

handler404 =  lambda request, exception=None: JsonResponse({
          "status": "error",
          "code": 404,
          "data": None,
          "message": "The resource was not found"
        })

handler500 =  lambda request, exception=None: JsonResponse({
          "status": "error",
          "code": 500,
          "data": None,
          "message": "Oops! Server experienced an error."
        })

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

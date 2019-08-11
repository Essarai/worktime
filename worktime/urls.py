from django.contrib import admin
from django.urls import include, path
import tinymce


urlpatterns = [
    path('worktime/', include('students.urls',namespace='worktime')),
    path('', include('students.urls')),
    path('tinymce/',include('tinymce.urls')),
    path('admin/', admin.site.urls),
]

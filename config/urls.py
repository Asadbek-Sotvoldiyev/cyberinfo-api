from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Cyberinfo.uz - Kiberxavfsizlik yangiliklarini ulashib boruvchi websayt uchun API",
      default_version='v1',
      description="Bu API kiberxavfsizlik yangiliklarini olish, boshqarish va yangilash uchun mo'ljallangan. Siz yangiliklarni ko'rish, qidirish va filtr qilish imkoniyatiga ega bo'lasiz. API yangiliklarni to'plash va foydalanuvchilarni eng so'nggi xavfsizlik tahdidlari bilan tanishtirishda yordam beradi.",
      terms_of_service="https://t.me/Asadbek_Sotvoldiyev",
      contact=openapi.Contact(email="blogasadbek@gmail.com"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('news/', include('news.urls')),
    path('videos/', include('videos.urls')),

    # swagger
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

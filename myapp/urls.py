from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('crawler/', views.page1_crawler, name='crawler'),
    path('transform/', views.page2_transform, name='transform'),
    # API接口
    path('api/crawler/', views.api_crawler, name='api_crawler'),
    path('api/transform/', views.api_transform, name='api_transform'),
]
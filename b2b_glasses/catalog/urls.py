from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # --- Пути для Оправ (уже были) ---
    path('frames/', views.FrameListView.as_view(), name='frame-list'),
    path('frames/filters/', views.FrameFilterOptionsView.as_view(),
         name='frame-filter-options'),

    # --- ДОБАВЬТЕ ЭТИ ПУТИ ДЛЯ ЛИНЗ ---
    path('lenses/', views.LensListView.as_view(), name='lens-list'),
    path('lenses/options/', views.LensOptionsView.as_view(), name='lens-options'),
]

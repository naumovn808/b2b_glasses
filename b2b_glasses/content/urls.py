from django.urls import path
from .views import (
    ContactsView, AboutUsView, TrainingListView,
    FAQListView, NewsListView
)

app_name = 'content'

urlpatterns = [
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('about/', AboutUsView.as_view(), name='about'),
    path('training/', TrainingListView.as_view(), name='training'),
    path('faq/', FAQListView.as_view(), name='faq'),
    path('news/', NewsListView.as_view(), name='news'),
]

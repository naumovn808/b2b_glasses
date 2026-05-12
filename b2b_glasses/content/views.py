from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Contacts, AboutUs, Training, FAQ, News
from .serializers import (
    ContactsSerializer, AboutUsSerializer,
    TrainingSerializer, FAQSerializer, NewsSerializer
)

# Используем AllowAny, так как эта информация обычно публичная


class ContactsView(generics.RetrieveAPIView):
    serializer_class = ContactsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return Contacts.get_solo()


class AboutUsView(generics.RetrieveAPIView):
    serializer_class = AboutUsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return AboutUs.get_solo()


class TrainingListView(generics.ListAPIView):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [AllowAny]


class TrainingDetailView(generics.RetrieveAPIView):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [AllowAny]


class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]


class NewsListView(generics.ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]


class NewsDetailView(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]

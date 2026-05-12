from rest_framework import serializers
from .models import Contacts, AboutUs, Certificate, Partner, Training, FAQ, News


class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = "__all__"


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["id", "title", "image"]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ["id", "name", "image", "link"]


class AboutUsSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True, read_only=True)
    partners = PartnerSerializer(many=True, read_only=True)

    class Meta:
        model = AboutUs
        fields = [
            "title",
            "title_ru",
            "title_en",
            "title_uz",
            "text",
            "certificates",
            "partners",
        ]


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = [
            "id",
            "title",
            "title_ru",
            "title_en",
            "title_uz",
            "image",
            "video",
            "description",
            "description_ru",
            "description_en",
            "description_uz",
            "order",
        ]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"

from django.contrib import admin
from solo.admin import SingletonModelAdmin
from modeltranslation.admin import TranslationAdmin
from .models import Contacts, AboutUs, Certificate, Partner, Training, FAQ, News

# Для Singletons + Translation нужно наследовать оба класса.
# Порядок важен: TranslationAdmin первый, потом SingletonModelAdmin (или ModelAdmin)


class ContactsAdmin(TranslationAdmin, SingletonModelAdmin):
    pass


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 1


class PartnerInline(admin.TabularInline):
    model = Partner
    extra = 1


class AboutUsAdmin(TranslationAdmin, SingletonModelAdmin):
    inlines = [CertificateInline, PartnerInline]


class TrainingAdmin(TranslationAdmin):
    list_display = ('title', 'order')


class FAQAdmin(TranslationAdmin):
    list_display = ('question', 'order')


class NewsAdmin(TranslationAdmin):
    list_display = ('title', 'created_at')


admin.site.register(Contacts, ContactsAdmin)
admin.site.register(AboutUs, AboutUsAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(News, NewsAdmin)

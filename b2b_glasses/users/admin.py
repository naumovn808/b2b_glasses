from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User, Company, TelegramLinkToken

# --- ИМПОРТЫ ДЛЯ UNREGISTER ---
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from catalog.models import (
    Brand, FrameMaterial, FrameShape, FrameType, FrameGender,
    FrameAgeGroup, Frame, LensSeries, Lens
)

# --- UNREGISTER LOGIC ---
if admin.site.is_registered(Group):
    admin.site.unregister(Group)

if admin.site.is_registered(Token):
    admin.site.unregister(Token)

if admin.site.is_registered(DjangoJob):
    admin.site.unregister(DjangoJob)

if admin.site.is_registered(DjangoJobExecution):
    admin.site.unregister(DjangoJobExecution)

if admin.site.is_registered(Brand):
    admin.site.unregister(Brand)
if admin.site.is_registered(FrameMaterial):
    admin.site.unregister(FrameMaterial)
if admin.site.is_registered(FrameShape):
    admin.site.unregister(FrameShape)
if admin.site.is_registered(FrameType):
    admin.site.unregister(FrameType)
if admin.site.is_registered(FrameGender):
    admin.site.unregister(FrameGender)
if admin.site.is_registered(FrameAgeGroup):
    admin.site.unregister(FrameAgeGroup)
if admin.site.is_registered(Frame):
    admin.site.unregister(Frame)
if admin.site.is_registered(LensSeries):
    admin.site.unregister(LensSeries)
if admin.site.is_registered(Lens):
    admin.site.unregister(Lens)


# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ССЫЛКИ ---
def get_telegram_link_html(user):
    """
    Генерирует HTML для копирования ссылки. 
    Вынесена отдельно, чтобы использовать и в UserAdmin, и в Inline.
    """
    if not user.pk:
        return "Сохраните пользователя, чтобы получить ссылку"

    if user.telegram_id:
        return "Аккаунт уже привязан"

    token_obj = TelegramLinkToken.objects.filter(user=user).first()

    # Благодаря сигналам, токен должен быть всегда. Но на всякий случай:
    if not token_obj:
        return "Токен не найден (попробуйте пересохранить)"

    bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'bot_username')
    link = f"https://t.me/{bot_username}?start={token_obj.token}"

    input_id = f"telegram-link-input-{user.pk}"
    feedback_id = f"telegram-link-feedback-{user.pk}"

    js_onclick = (
        f"var input = document.getElementById('{input_id}');"
        f"var feedback = document.getElementById('{feedback_id}');"
        "input.select();"
        "input.setSelectionRange(0, 99999);"
        "document.execCommand('copy');"
        "feedback.style.display = 'inline';"
        "feedback.style.opacity = '1';"
        "setTimeout(function() {{"
        "  feedback.style.opacity = '0';"
        "  setTimeout(function() {{ feedback.style.display = 'none'; }}, 500);"
        "}}, 2000);"
    ).replace('"', '&quot;')

    html_output = f"""
        <div style="display: flex; align-items: center; position: relative;">
            <span 
                onclick="{js_onclick}"
                title="Нажмите, чтобы скопировать"
                style="color: var(--link-color, #007bff); cursor: pointer; text-decoration: underline; font-weight: 500;"
            >
                Скопировать ссылку
            </span>
            <span id="{feedback_id}" style="margin-left: 10px; color: green; font-weight: bold; display: none; opacity: 0; transition: opacity 0.5s;">
                Скопировано!
            </span>
            <input type="text" value="{link}" id="{input_id}" style="position:absolute; left:-9999px; top:0px; opacity:0;">
        </div>
    """
    return format_html(html_output)


class UserInline(admin.TabularInline):
    """
    Инлайн пользователей внутри Компании.
    """
    model = User
    fields = ('username', 'first_name', 'last_name',
              'is_active', 'telegram_link_display')
    readonly_fields = ('telegram_link_display',)
    can_delete = True
    extra = 1
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return True

    def telegram_link_display(self, obj):
        return get_telegram_link_html(obj)

    telegram_link_display.short_description = "Ссылка Telegram"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'inn', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'external_id', 'inn', 'partner_name', 'head_partner_name')
    inlines = [UserInline]


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username',)


class AssignedCompanyFilter(admin.SimpleListFilter):
    title = _('Компания')
    parameter_name = 'company_assigned'

    def lookups(self, request, model_admin):
        return (('yes', _('Назначенные')), ('no', _('Не назначенные')),)

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(company__isnull=False)
        if self.value() == 'no':
            return queryset.filter(company__isnull=True)


class UserAdminCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'company')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm
    list_display = (
        'username', 'company', 'telegram_id',
        'telegram_username', 'is_active'
    )
    list_filter = (AssignedCompanyFilter, 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'is_active')}),
        ('Персональная информация', {'fields': (
            'company', 'first_name', 'last_name', 'email'
        )}),
        ('Telegram (заполняется автоматически)', {'fields': (
            'telegram_id', 'telegram_username', 'telegram_first_name',
            'telegram_last_name', 'phone_number', 'generated_telegram_link'
        )}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'company')}),
    )
    readonly_fields = ('generated_telegram_link',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.GET.get('all') is None:
            qs = qs.exclude(is_superuser=True)
        return qs

    # Мы убрали save_model, так как теперь всю работу делает signal в signals.py!

    def generated_telegram_link(self, obj):
        return get_telegram_link_html(obj)

    generated_telegram_link.short_description = "Ссылка для привязки Telegram"

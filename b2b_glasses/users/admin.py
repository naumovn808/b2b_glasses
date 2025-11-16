from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User, Company, TelegramLinkToken

# --- 1. ИМПОРТИРУЕМ ВСЕ, ЧТО ХОТИМ СПРЯТАТЬ ---
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from catalog.models import (
    Brand, FrameMaterial, FrameShape, FrameType, FrameGender,
    FrameAgeGroup, Frame, LensSeries, Lens
)

# --- 2. "ПРЯЧЕМ" ИХ (UNREGISTER) С ПРОВЕРКОЙ ---
# (Это исправит ошибку "NotRegistered")

if admin.site.is_registered(Group):
    admin.site.unregister(Group)

if admin.site.is_registered(Token):
    admin.site.unregister(Token)

if admin.site.is_registered(DjangoJob):
    admin.site.unregister(DjangoJob)

if admin.site.is_registered(DjangoJobExecution):
    admin.site.unregister(DjangoJobExecution)

# (На тот случай, если 'catalog' загрузится раньше)
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
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---


class UserInline(admin.TabularInline):
    """
    "Инлайн" для отображения и ДОБАВЛЕНИЯ Пользователей
    ВНУТРИ страницы Компании.
    """
    model = User
    fields = ('username', 'is_active', 'first_name', 'last_name')
    readonly_fields = ()
    can_delete = True
    extra = 1
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return True


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [UserInline]


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username',)

# ... (AssignedCompanyFilter и UserAdminCreationForm остаются без изменений) ...


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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and not obj.telegram_id:
            TelegramLinkToken.objects.get_or_create(user=obj)

    def generated_telegram_link(self, obj):
        """
        (v19) Показывает элегантную ссылку, которая
        копируется в буфер при клике.
        """
        if obj.telegram_id:
            return "Аккаунт уже привязан"

        token_obj = TelegramLinkToken.objects.filter(user=obj).first()
        if not token_obj:
            return "Нажмите 'Сохранить', чтобы сгенерировать токен"

        bot_username = settings.TELEGRAM_BOT_USERNAME
        link = f"https://t.me/{bot_username}?start={token_obj.token}"

        # Уникальные ID для HTML-элементов этого пользователя
        input_id = f"telegram-link-input-{obj.pk}"
        feedback_id = f"telegram-link-feedback-{obj.pk}"

        # JavaScript, который будет выполнен при нажатии.
        # Он находит невидимый input, копирует его
        # и показывает "красивое сообщение"
        js_onclick = (
            f"var input = document.getElementById('{input_id}');"
            f"var feedback = document.getElementById('{feedback_id}');"
            "input.select();"
            "input.setSelectionRange(0, 99999);"  # Для мобильных
            "document.execCommand('copy');"
            # Показываем "Скопировано!"
            "feedback.style.display = 'inline';"
            "feedback.style.opacity = '1';"
            # Прячем "Скопировано!" через 2 секунды
            "setTimeout(function() {{"
            "  feedback.style.opacity = '0';"
            "  setTimeout(function() {{ feedback.style.display = 'none'; }}, 500);"
            "}}, 2000);"
        ).replace('"', '&quot;')  # Экранируем кавычки для HTML

        # HTML-вывод:
        html_output = f"""
            <div style="display: flex; align-items: center; position: relative;">
                
                <span 
                    onclick="{js_onclick}"
                    title="Нажмите, чтобы скопировать"
                    style="color: var(--link-color, #007bff); 
                        cursor: pointer; 
                        text-decoration: underline; 
                        font-weight: 500;"
                >
                    {link}
                </span>

                <span 
                    id="{feedback_id}" 
                    style="margin-left: 15px; 
                        color: var(--success-color, green); 
                        font-weight: bold; 
                        display: none; 
                        opacity: 0;
                        transition: opacity 0.5s ease;"
                >
                    Скопировано!
                </span>

                <input 
                    type="text" 
                    value="{link}" 
                    id="{input_id}" 
                    style="position:absolute; left:-9999px; top:0px; opacity:0;"
                >
            </div> """

        return format_html(html_output)

    generated_telegram_link.short_description = "Ссылка для привязки Telegram"

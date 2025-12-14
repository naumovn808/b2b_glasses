from modeltranslation.translator import register, TranslationOptions
from .models import Contacts, AboutUs, Training, FAQ, News


@register(Contacts)
class ContactsTranslationOptions(TranslationOptions):
    fields = ('address_label', 'work_hours')


@register(AboutUs)
class AboutUsTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(Training)
class TrainingTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

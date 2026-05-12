# Сводка изменений

## CORS

Файл:

- `b2b_glasses/b2b_glasses/settings.py`

Что изменили:

- Временно разрешили CORS с любого origin:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

Зачем:

- Фронтенд ходил на API с другого origin и мог получать CORS-блокировку.
- После изменения ответы содержат:

```http
access-control-allow-origin: *
```

Важно:

- Это временная настройка. Для продакшена лучше вернуть whitelist через `CORS_ALLOWED_ORIGINS`.

## 403 На Каталоге

Файл:

- `b2b_glasses/catalog/views.py`

Проблема:

- Запросы вроде:

```text
GET /api/v1/catalog/frames/filters/
```

возвращали `403 Forbidden`.

Причина:

- Catalog endpoints требовали авторизацию:

```python
permission_classes = [IsAuthenticated | IsBot]
```

- Фронтенд отправлял запросы без `Authorization`, поэтому Django REST Framework блокировал доступ.

Что изменили:

- Для публичных catalog endpoints поставили:

```python
permission_classes = [AllowAny]
```

Теперь без авторизации доступны:

```text
GET /api/v1/catalog/frames/
GET /api/v1/catalog/frames/filters/
GET /api/v1/catalog/lenses/
GET /api/v1/catalog/lenses/options/
GET /api/v1/catalog/products/<product_type>/<id>/
```

## Единый Endpoint Продукта

Файлы:

- `b2b_glasses/catalog/views.py`
- `b2b_glasses/catalog/urls.py`
- `frontend/src/entities/catalog/api/catalogApi.ts`
- `frontend/src/entities/catalog/model/types.ts`
- `frontend/src/entities/catalog/index.ts`
- `frontend/src/pages/Catalog/ProductDetailsPage/ui/ProductDetailsPage.tsx`

Что добавили:

```text
GET /api/v1/catalog/products/frame/<id>/
GET /api/v1/catalog/products/lens/<id>/
```

Формат ответа:

```json
{
  "type": "frame",
  "item": {
    "id": 1,
    "name": "Minimo Classic 2101 C1",
    "price": "420000.00"
  }
}
```

Что убрали:

```text
GET /api/v1/catalog/frames/<id>/
GET /api/v1/catalog/lenses/<id>/
```

Эти старые detail routes теперь должны отдавать `404`.

Фронт:

- Вместо двух hooks `useGetFrameByIdQuery` и `useGetLensByIdQuery` используется один:

```ts
useGetProductByIdQuery({ type, id });
```

## About Us

Файлы:

- `b2b_glasses/content/models.py`
- `b2b_glasses/content/translation.py`
- `b2b_glasses/content/serializers.py`
- `b2b_glasses/content/migrations/0003_aboutus_title_training_video.py`
- `frontend/src/entities/about/model/types.ts`
- `frontend/src/pages/AboutUsPage/AboutUsPage.tsx`

Что добавили:

- Поле `title` для блока About Us.
- Переводы:

```text
title_ru
title_en
title_uz
```

- API теперь отдаёт `title`.
- Фронт показывает заголовок из админки, если он заполнен.

## Обучение И Видео

Файлы:

- `b2b_glasses/content/models.py`
- `b2b_glasses/content/migrations/0003_aboutus_title_training_video.py`
- `frontend/src/entities/training/model/types.ts`
- `frontend/src/pages/Education/EducationArticlePage/ui/EducationArticlePage.tsx`

Что добавили:

## Видео для Training

Файлы:

- `b2b_glasses/content/models.py` (добавлена функция `validate_video_file` и validators в Training)
- `b2b_glasses/content/serializers.py`
- `b2b_glasses/content/views.py`
- `frontend/src/entities/training/model/types.ts`
- `frontend/src/pages/Education/EducationArticlePage/ui/EducationArticlePage.tsx`

Что добавили:

- Функция `validate_video_file()` которая:
  - Проверяет расширение файла (mp4, webm, ogg, mov, avi, flv, mkv)
  - Проверяет максимальный размер (100 МБ)
  - Выбрасывает `ValidationError` если условия не выполнены

- Поле `video` в модель `Training` с валидацией:

```python
video = models.FileField(
    "Видео",
    upload_to='training/videos/',
    blank=True,
    null=True,
    validators=[validate_video_file],
    help_text="Поддерживаемые форматы: MP4, WebM, OGG, MOV, AVI, FLV, MKV. Максимальный размер: 100 МБ"
)
```

- Фронт теперь подставляет `training.video` в `<video controls>`.
- Если видео не загружено, видеоблок не показывается.

### Валидация

При попытке загрузить видео неподдерживаемого формата или размером более 100 МБ, админка покажет ошибку валидации.

## Detail API Для News И Training

Файлы:

- `b2b_glasses/content/views.py`
- `b2b_glasses/content/urls.py`
- `frontend/src/entities/news/api/newsApi.ts`
- `frontend/src/entities/news/index.ts`
- `frontend/src/entities/training/api/trainingApi.ts`
- `frontend/src/entities/training/index.ts`
- `frontend/src/pages/News/NewsArticlePage/ui/NewsArticlePage.tsx`
- `frontend/src/pages/Education/EducationArticlePage/ui/EducationArticlePage.tsx`

Что добавили:

```text
GET /api/v1/content/news/<id>/
GET /api/v1/content/training/<id>/
```

Фронт:

- Страница новости `/news/:newsId` теперь грузит новость по id из API.
- Страница обучения `/education/:educationSlug` теперь грузит обучение по id из API.
- Раньше страницы зависели от уже загруженного списка в RTK Query cache.

## Демо-Данные Каталога

Файл:

- `b2b_glasses/catalog/management/commands/seed_catalog_data.py`

Что добавили:

- Management command для наполнения каталога демо-данными:

```bash
python manage.py seed_catalog_data
```

Добавляет:

- бренды;
- материалы;
- формы;
- типы оправ;
- пол;
- возрастные группы;
- серии линз;
- оправы;
- линзы.

Команда уже запускалась в контейнере:

```bash
docker compose exec web python manage.py seed_catalog_data
```

После добавления цветов команда также создаёт демо-цвета для продуктов.

## Цвета И Фото Продуктов

Файлы:

- `b2b_glasses/catalog/models.py`
- `b2b_glasses/catalog/admin.py`
- `b2b_glasses/catalog/serializers.py`
- `b2b_glasses/catalog/migrations/0002_productcolor_productimage.py`
- `b2b_glasses/catalog/management/commands/seed_catalog_data.py`
- `frontend/src/entities/catalog/model/types.ts`
- `frontend/src/features/product-card/model/types.ts`
- `frontend/src/pages/Catalog/CatalogPage/model/catalogApiMappers.ts`
- `frontend/src/pages/Catalog/ProductDetailsPage/ui/ProductDetailsPage.tsx`

Что добавили:

- `ProductColor` для нескольких цветов продукта.
- `ProductImage` для нескольких фото продукта.
- Обе модели работают и для `Frame`, и для `Lens` через `GenericForeignKey` / `GenericRelation`.

### Цвета

В админке у `Frame` и `Lens` появился inline-блок `Цвета продуктов`.

Можно добавить несколько цветов:

```text
name
hex_value
order
```

Поле `hex_value` в админке сделано как color picker:

```python
forms.TextInput(attrs={'type': 'color'})
```

API теперь отдаёт:

```json
"colors": [
  {
    "id": 1,
    "name": "Черный глянец",
    "hex_value": "#111111",
    "order": 0
  }
]
```

### Фото

В админке у `Frame` и `Lens` появился inline-блок `Фото продуктов`.

Можно добавить несколько фото:

```text
image
order
```

Файлы загружаются в:

```text
media/products/
```

API теперь отдаёт:

```json
"images": [
  {
    "id": 1,
    "image": "/media/catalog/products/example.jpg",
    "order": 0
  }
]
```

### Фронт

Фронт теперь учитывает новые поля:

- если у продукта есть `images`, первое фото используется как основное изображение карточки;
- на странице продукта галерея строится из всех `images`;
- если у продукта есть `colors`, они используются вместо старых полей цвета продукта;
- если `images` или `colors` пустые, остаются старые fallback-значения.

Фото через seed не добавляются, их нужно загружать вручную через админку.

Позже удалили лишние поля:

- `Frame.color_code`, потому что цвета теперь хранятся в `ProductColor`;
- `Frame.color_name`, потому что название цвета тоже больше не заполняется вручную;
- `ProductImage.alt`, потому что alt-текст для фото продукта решили не заполнять в админке.
- `ProductColor.name` сначала удаляли, затем вернули по требованию: названия цветов теперь хранятся только в блоке `ProductColor`, не в самой оправе.

Миграция удаления:

- `b2b_glasses/catalog/migrations/0003_remove_frame_color_code_remove_productimage_alt.py`
- `b2b_glasses/catalog/migrations/0004_remove_productcolor_name.py`
- `b2b_glasses/catalog/migrations/0005_remove_frame_color_name.py`
- `b2b_glasses/catalog/migrations/0007_productcolor_name.py`

## Проверки

Запускались проверки:

```bash
docker compose exec web python manage.py check
npx tsc -b
```

Результат:

- Django check проходит.
- TypeScript check проходит.
- Остался старый warning проекта про устаревший CKEditor 4:

```text
ckeditor.W001
```

Он не связан с текущими изменениями.

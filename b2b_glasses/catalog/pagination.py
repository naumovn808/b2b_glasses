from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Кастомный класс пагинации, который позволяет фронтенду
    задавать размер страницы (page_size).
    """
    # 1. Размер страницы по умолчанию (если ?page_size= не указан)
    # (Мы оставляем 5, как и было, т.к. бот полагается на это)
    page_size = 5

    # 2. Имя параметра, который ищет фронтенд
    # (напр. ?page_size=10)
    page_size_query_param = 'page_size'

    # 3. Максимальный размер страницы, который мы разрешаем.
    # (Защита, чтобы фронтенд не запросил ?page_size=100000)
    max_page_size = 100

    def get_page_size(self, request):
        # Эта функция логирует, если размер страницы был изменен
        page_size_str = request.query_params.get(self.page_size_query_param)
        if page_size_str:
            try:
                page_size_int = int(page_size_str)
                # Проверка на максимум
                if page_size_int > self.max_page_size:
                    logger.warning(
                        f"Запрошен page_size={page_size_int}, но max_page_size={self.max_page_size}. Возвращаю max.")
                    return self.max_page_size
                # Проверка на минимум
                elif page_size_int <= 0:
                    logger.warning(
                        f"Запрошен некорректный page_size={page_size_int}. Возвращаю по умолчанию.")
                    return self.page_size
                else:
                    # Используем кастомный размер
                    logger.debug(
                        f"Используется кастомный page_size={page_size_int}")
                    return page_size_int
            except (ValueError, TypeError):
                logger.warning(
                    f"Запрошен некорректный page_size='{page_size_str}'. Возвращаю по умолчанию.")
                pass

        # Если ?page_size= не указан, используем стандартный
        return self.page_size

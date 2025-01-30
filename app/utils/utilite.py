import re

def extract_options(query: str) -> list:
    """
    Извлечение вариантов ответов из текста запроса.
    Формат:
    1. Вариант 1
    2. Вариант 2
    """
    pattern = r'(\d+)\.\s*(.+)'
    matches = re.findall(pattern, query)
    if matches:
        return matches
    return []
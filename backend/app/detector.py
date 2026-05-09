"""
detector.py — определяет тип IOC.
Используем регулярные выражения (regex) для распознавания:
- IP адрес (например: 8.8.8.8)
- Domain (например: evil.com)
- URL (например: http://evil.com/malware)
- Hash MD5/SHA1/SHA256
- unknown — если ничего не подошло
"""

import re


def detect_ioc_type(ioc: str) -> str:
    """
    Принимает строку IOC и возвращает её тип.
    Порядок проверок важен: URL проверяем до domain.
    """

    ioc = ioc.strip()

    # URL — начинается с http:// или https://
    url_pattern = re.compile(
        r'^https?://'          # Обязательный протокол
        r'[^\s/$.?#]'          # Первый символ домена
        r'[^\s]*$',            # Остаток URL
        re.IGNORECASE
    )
    if url_pattern.match(ioc):
        return "url"

    # IP адрес — четыре числа от 0 до 255, разделённые точками
    ip_pattern = re.compile(
        r'^(\d{1,3}\.){3}\d{1,3}$'
    )
    if ip_pattern.match(ioc):
        # Дополнительная проверка: каждый октет ≤ 255
        parts = ioc.split(".")
        if all(0 <= int(p) <= 255 for p in parts):
            return "ip"

    # Hash:
    # MD5    — 32 hex символа
    # SHA1   — 40 hex символа
    # SHA256 — 64 hex символа
    hash_pattern = re.compile(
        r'^[a-fA-F0-9]{32}$|'   # MD5
        r'^[a-fA-F0-9]{40}$|'   # SHA1
        r'^[a-fA-F0-9]{64}$',   # SHA256
        re.IGNORECASE
    )
    if hash_pattern.match(ioc):
        return "hash"

    # Domain — содержит точку, без пробелов, без протокола
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9]'        # Начало метки
        r'(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
        r'\.)'                     # Точка между метками
        r'+[a-zA-Z]{2,}$'         # TLD минимум 2 символа
    )
    if domain_pattern.match(ioc):
        return "domain"

    return "unknown"

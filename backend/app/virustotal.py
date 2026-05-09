"""
virustotal.py — интеграция с VirusTotal API v3.
Разные типы IOC отправляются на разные endpoints:
- IP      → /ip_addresses/{ip}
- Domain  → /domains/{domain}
- URL     → /urls (сначала submit, потом получаем анализ)
- Hash    → /files/{hash}

Документация: https://developers.virustotal.com/reference
"""

import os
import httpx                   # Async HTTP клиент (лучше requests для FastAPI)
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем API ключ из переменных окружения
VT_API_KEY = os.getenv("VT_API_KEY")

# Базовый URL VirusTotal API v3
VT_BASE_URL = "https://www.virustotal.com/api/v3"


async def lookup_virustotal(ioc: str, ioc_type: str) -> dict:
    """
    Делает запрос к VirusTotal в зависимости от типа IOC.
    Возвращает словарь со статистикой или ошибкой.
    """

    if not VT_API_KEY:
        return {"error": "VT_API_KEY is not set. Please configure your .env file."}

    # Заголовки для аутентификации в VirusTotal
    headers = {
        "x-apikey": VT_API_KEY,
        "Accept": "application/json"
    }

    try:
        # Используем async HTTP клиент с таймаутом 15 секунд
        async with httpx.AsyncClient(timeout=15.0) as client:

            if ioc_type == "ip":
                response = await client.get(
                    f"{VT_BASE_URL}/ip_addresses/{ioc}",
                    headers=headers
                )

            elif ioc_type == "domain":
                response = await client.get(
                    f"{VT_BASE_URL}/domains/{ioc}",
                    headers=headers
                )

            elif ioc_type == "hash":
                response = await client.get(
                    f"{VT_BASE_URL}/files/{ioc}",
                    headers=headers
                )

            elif ioc_type == "url":
                # URL требует двух шагов:
                # 1. Отправляем URL на сканирование (POST /urls)
                # 2. Получаем результат по ID анализа
                import base64
                # VirusTotal требует URL в base64 без padding
                url_id = base64.urlsafe_b64encode(ioc.encode()).decode().rstrip("=")
                response = await client.get(
                    f"{VT_BASE_URL}/urls/{url_id}",
                    headers=headers
                )
            else:
                return {"error": f"Unsupported IOC type: {ioc_type}"}

            # Обрабатываем статус ответа
            if response.status_code == 200:
                data = response.json()
                return parse_vt_response(data)

            elif response.status_code == 404:
                return {"error": "IOC not found in VirusTotal database. It may be clean or never analyzed."}

            elif response.status_code == 401:
                return {"error": "Invalid VirusTotal API key. Check your VT_API_KEY in .env"}

            elif response.status_code == 429:
                return {"error": "VirusTotal rate limit exceeded. Free tier allows 4 requests/minute. Please wait and try again."}

            else:
                return {"error": f"VirusTotal returned unexpected status: {response.status_code}"}

    except httpx.TimeoutException:
        return {"error": "Request to VirusTotal timed out. Please try again."}

    except httpx.RequestError as e:
        return {"error": f"Network error contacting VirusTotal: {str(e)}"}


def parse_vt_response(data: dict) -> dict:
    """
    Извлекаем нужные поля из ответа VirusTotal.
    Структура ответа: data → attributes → last_analysis_stats
    """

    try:
        attributes = data.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})

        return {
            "stats": {
                "malicious":  stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless":   stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
            }
        }

    except Exception as e:
        return {"error": f"Failed to parse VirusTotal response: {str(e)}"}

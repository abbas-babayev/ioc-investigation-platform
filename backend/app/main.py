"""
main.py — точка входа FastAPI приложения.
Здесь мы создаём сервер, настраиваем CORS и регистрируем endpoint /api/lookup.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.detector import detect_ioc_type
from app.virustotal import lookup_virustotal
from app.scoring import calculate_risk

# Создаём FastAPI приложение
app = FastAPI(
    title="IOC Investigation Platform",
    description="SOC tool for IOC enrichment via VirusTotal",
    version="1.0.0"
)

# CORS позволяет браузеру (frontend) обращаться к нашему API
# Без этого браузер заблокирует запросы с другого порта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # В production замени на конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модель входящих данных — FastAPI автоматически валидирует JSON
class IOCRequest(BaseModel):
    ioc: str  # Строка с IP, domain, URL или hash


@app.get("/")
def root():
    """Простой health check endpoint."""
    return {"status": "ok", "message": "IOC Investigation Platform is running"}


@app.post("/api/lookup")
async def lookup_ioc(request: IOCRequest):
    """
    Основной endpoint.
    1. Получаем IOC из запроса
    2. Определяем тип (IP / domain / URL / hash / unknown)
    3. Делаем запрос к VirusTotal
    4. Считаем risk score
    5. Возвращаем результат
    """

    ioc = request.ioc.strip()  # Убираем пробелы по краям

    if not ioc:
        raise HTTPException(status_code=400, detail="IOC cannot be empty")

    # Шаг 1: Определяем тип IOC
    ioc_type = detect_ioc_type(ioc)

    if ioc_type == "unknown":
        return {
            "ioc": ioc,
            "ioc_type": "unknown",
            "error": "Could not determine IOC type. Please check your input.",
            "stats": None,
            "risk_level": None,
            "recommendation": "Verify the IOC format and try again."
        }

    # Шаг 2: Запрашиваем данные из VirusTotal
    vt_result = await lookup_virustotal(ioc, ioc_type)

    if "error" in vt_result:
        return {
            "ioc": ioc,
            "ioc_type": ioc_type,
            "error": vt_result["error"],
            "stats": None,
            "risk_level": None,
            "recommendation": "VirusTotal lookup failed. Check your API key or try again later."
        }

    # Шаг 3: Считаем риск
    stats = vt_result.get("stats", {})
    risk_level, recommendation = calculate_risk(stats)

    return {
        "ioc": ioc,
        "ioc_type": ioc_type,
        "stats": stats,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "error": None
    }

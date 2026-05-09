/**
 * app.js — логика фронтенда.
 * Отправляет IOC на backend, получает результат и отображает его.
 *
 * ВАЖНО: Замени API_URL на адрес своего backend!
 * - Без Docker: http://localhost:8000
 * - С Docker:   http://localhost:8000 (по умолчанию)
 */

// URL нашего backend API
const API_URL = "http://localhost:8000";

/**
 * Основная функция — вызывается при нажатии кнопки INVESTIGATE
 * или при нажатии Enter в поле ввода.
 */
async function investigate() {
  // Получаем введённый IOC
  const ioc = document.getElementById("iocInput").value.trim();

  // Проверяем, что поле не пустое
  if (!ioc) {
    showError("Please enter an IOC to investigate.");
    return;
  }

  // Скрываем предыдущие результаты и показываем загрузку
  hideAll();
  showLoading(true);
  setButtonDisabled(true);

  try {
    // Отправляем POST запрос на backend
    const response = await fetch(`${API_URL}/api/lookup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ ioc: ioc })
    });

    // Парсим JSON ответ
    const data = await response.json();

    // Если HTTP ответ не 200–299 — это ошибка сервера
    if (!response.ok) {
      showError(data.detail || "Server returned an error. Please try again.");
      return;
    }

    // Если в ответе есть поле error — показываем его
    if (data.error) {
      showError(data.error);
      return;
    }

    // Успех — отображаем результат
    showResult(data);

  } catch (err) {
    // Сетевая ошибка (backend недоступен)
    if (err.name === "TypeError" && err.message.includes("fetch")) {
      showError(
        "Cannot connect to the backend server. " +
        "Make sure it is running on " + API_URL + ". " +
        "Run: uvicorn app.main:app --reload"
      );
    } else {
      showError("Unexpected error: " + err.message);
    }
  } finally {
    // Всегда скрываем спиннер и разблокируем кнопку
    showLoading(false);
    setButtonDisabled(false);
  }
}


/**
 * Заполняет и показывает блок с результатом.
 * @param {Object} data — JSON ответ от backend
 */
function showResult(data) {
  // IOC и тип
  document.getElementById("resIoc").textContent   = data.ioc   || "—";
  document.getElementById("resType").textContent  = data.ioc_type
    ? data.ioc_type.toUpperCase()
    : "—";

  // Статистика детекций
  const stats = data.stats || {};
  document.getElementById("statMalicious").textContent  = stats.malicious  ?? "—";
  document.getElementById("statSuspicious").textContent = stats.suspicious ?? "—";
  document.getElementById("statHarmless").textContent   = stats.harmless   ?? "—";
  document.getElementById("statUndetected").textContent = stats.undetected ?? "—";

  // Risk badge
  const badge = document.getElementById("riskBadge");
  const risk  = data.risk_level || "Unknown";
  badge.textContent = risk;
  // Убираем старые классы и добавляем новый
  badge.className = "risk-badge " + risk;

  // Рекомендация
  document.getElementById("resRecommendation").textContent =
    data.recommendation || "No recommendation available.";

  // Показываем блок результата
  document.getElementById("resultBlock").classList.remove("hidden");
}


/**
 * Показывает сообщение об ошибке.
 * @param {string} message
 */
function showError(message) {
  document.getElementById("errorMsg").textContent = message;
  document.getElementById("errorBlock").classList.remove("hidden");
}


/**
 * Управляет видимостью спиннера загрузки.
 * @param {boolean} visible
 */
function showLoading(visible) {
  const el = document.getElementById("loadingBlock");
  if (visible) {
    el.classList.remove("hidden");
  } else {
    el.classList.add("hidden");
  }
}


/**
 * Скрывает все блоки результата/ошибки.
 */
function hideAll() {
  document.getElementById("resultBlock").classList.add("hidden");
  document.getElementById("errorBlock").classList.add("hidden");
  document.getElementById("loadingBlock").classList.add("hidden");
}


/**
 * Блокирует/разблокирует кнопку Investigate.
 * @param {boolean} disabled
 */
function setButtonDisabled(disabled) {
  document.getElementById("investigateBtn").disabled = disabled;
}


// Позволяем нажимать Enter для запуска расследования
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("iocInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      investigate();
    }
  });
});

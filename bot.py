import os
import asyncio
from textwrap import shorten

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv
from newsapi import NewsApiClient
from requests.exceptions import RequestException

# ---------- Настройка окружения и клиентов ----------
load_dotenv()

TG_TOKEN = os.getenv('BOT_TOKEN')
NEWS_API_KEY = os.getenv('API_NEWS')

if not TG_TOKEN:
    raise RuntimeError("Отсутствует TELEGRAM_BOT_TOKEN в .env")

if not NEWS_API_KEY:
    raise RuntimeError("Отсутствует API_NEWS в .env")

bot = Bot(
    token=TG_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Клиент NewsAPI (синхронный)
news_client = NewsApiClient(api_key=NEWS_API_KEY)

# ---------- Логика поиска ----------
def search_news_sync(query: str, language: str = "ru", limit: int = 3):
    """
    Синхронный вызов NewsAPI.
    Возвращает список словарей с title, description, url.
    Бросает исключения при сетевых/API ошибках.
    """
    response = news_client.get_everything(
        q=query,
        language=language,     # "ru" для русскоязычных; можно сменить на "en"
        sort_by="relevancy",
        page_size=limit
    )
    articles = response.get("articles", []) or []
    result = []
    for a in articles[:limit]:
        result.append({
            "title": a.get("title") or "Без заголовка",
            "description": a.get("description") or "Без описания",
            "url": a.get("url") or ""
        })
    return result

async def search_news(query: str, language: str = "ru", limit: int = 3):
    """
    Обёртка для вызова синхронной функции в отдельном потоке,
    чтобы не блокировать event loop aiogram.
    """
    return await asyncio.to_thread(search_news_sync, query, language, limit)

def format_article(idx: int, article: dict) -> str:
    title = article["title"].strip()
    desc = shorten((article["description"] or "").strip(), width=280, placeholder=" …")
    url = article["url"].strip()
    parts = [
        f"<b>Новость {idx}.</b> {title}",
        f"{desc}" if desc else "",
        f"{url}" if url else ""
    ]
    # Удаляем пустые строки
    return "\n".join(p for p in parts if p)

# ---------- Хендлеры ----------
@dp.message(CommandStart())
async def on_start(message: Message):
    await message.answer(
        "Привет! Напиши тему, и я найду новости по ней через NewsAPI."
    )

@dp.message(Command("help"))
async def on_help(message: Message):
    await message.answer(
        "Просто пришли текст запроса. Я верну новости по этой теме."
    )

@dp.message(F.text & ~F.via_bot)
async def on_query(message: Message):
    query = (message.text or "").strip()
    if not query:
        await message.answer("Тема не может быть пустой.")
        return

    try:
        articles = await search_news(query=query, language="ru", limit=3)

        if not articles:
            await message.answer(f"По теме «{query}» ничего не найдено.")
            return

        chunks = [format_article(i, a) for i, a in enumerate(articles, start=1)]
        text = "\n\n".join(chunks)

        # Telegram ограничивает длину сообщения ~4096 символами.
        if len(text) > 3800:
            text = text[:3800] + "\n\n…Слишком длинный вывод, часть урезана."

        await message.answer(text)

    except RequestException as e:
        await message.answer(f"Ошибка сети при обращении к NewsAPI: {e}")
    except Exception as e:
        # Логичнее логировать e, но для краткости показываем пользователю.
        await message.answer(f"Произошла ошибка: {e}")

# ---------- Точка входа ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

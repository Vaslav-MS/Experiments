import os
from newsapi import NewsApiClient
from requests.exceptions import RequestException
from dotenv import load_dotenv

def main():
    load_dotenv()
    API_KEY = os.getenv("API_NEWS")

    if not API_KEY:
        print("Ошибка: API-ключ не найден в .env (переменная NEWS_API_KEY).")
        return

    newsapi = NewsApiClient(api_key=API_KEY)

    query = input("Введите тему, по которой искать новости: ").strip()

    if not query:
        print("Тема не может быть пустой.")
        return

    try:
        response = newsapi.get_everything(
            q=query,
            language="ru",   # можно поставить "en", если нужны англоязычные
            sort_by="relevancy",
            page_size=5      # максимум 5 статей
        )

        articles = response.get("articles", [])
        if not articles:
            print(f"По теме '{query}' ничего не найдено.")
            return

        for i, article in enumerate(articles[:5], start=1):
            print(f"\nНовость {i}:")
            print(f"Заголовок: {article.get('title')}")
            print(f"Описание: {article.get('description')}")
            print(f"Ссылка: {article.get('url')}")

    except RequestException as e:
        print("Ошибка при подключении к API:", e)
    except Exception as e:
        print("Произошла ошибка:", e)

if __name__ == "__main__":
    main()

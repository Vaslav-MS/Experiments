import os
import requests
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from IPython.display import display, Image

load_dotenv()
API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")

query = "рентген легких"
num_images = 20

service = build("customsearch", "v1", developerKey=API_KEY)

def google_image_search(query, num_results):
    image_urls = []
    start_index = 1
    while len(image_urls) < num_results:
        num = min(10, num_results - len(image_urls))
        res = service.cse().list(
            q=query,
            cx=CX,
            searchType='image',
            num=num,
            start=start_index
        ).execute()

        for item in res.get('items', []):
            image_urls.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'mime': item.get('mime'),
                'width': item.get('image', {}).get('width'),
                'height': item.get('image', {}).get('height')
            })
        start_index += num
    return image_urls

print("Ищем изображения...")
images = google_image_search(query, num_images)

df = pd.DataFrame(images)
display(df)

df.to_csv("images_info.csv", index=False, encoding='utf-8')
print("Информация об изображениях сохранена в images_info.csv")

images_dir = "downloaded_images"
os.makedirs(images_dir, exist_ok=True)

def download_image(url, path):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Скачано: {path}")
    except Exception as e:
        print(f"Ошибка при скачивании {url}: {e}")

print("Скачиваем изображения...")
for idx, row in df.iterrows():
    image_url = row['link']


    file_extension = os.path.splitext(image_url)[1]
    if not file_extension.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
        file_extension = ".jpg"
    file_name = f"image_{idx+1}{file_extension}"
    file_path = os.path.join(images_dir, file_name)
    download_image(image_url, file_path)

print("Скачивание завершено.")

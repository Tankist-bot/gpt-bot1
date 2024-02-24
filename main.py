# Получение картинок по ключевому слову "moon"

import requests

name = input("Выберите имя из списка: tom, alex, ivan, oleg ")

location = input("Выберите локацию из списка: moon, mars, jupiter, saturn ")

url = "https://images-api.nasa.gov/search"

params = {
    "location": location,
    "page": "1",
    "media_type": "image",
    "year_start": "1920",
    "year_end": "2020"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    images = response.json()["collection"]["items"]
    print(images)
    i=0
    for image in images:
        i+=1
        image_url = image["links"][0]["href"]
        print(image_url)
        if i == 10:
            break
else:
    print("Ошибка:", response.json())


# Получение фотографии по nasa_id (можно найти в предыдущем запросе)
# В разном качестве (миниатюра, оригинал)

# import requests
#
# nasa_id = "PIA12870"
# url = f"https://images-api.nasa.gov/asset/{nasa_id}"
#
# response = requests.get(url)
#
# if response.status_code == 200:
#     print(response.json()["collection"]["items"][0]['href'])
# else:
#     print("Ошибка:", response.json())
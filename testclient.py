import requests
import json

# мок пост реквеста на сервис

url = 'http://127.0.0.1:5000/recommend'

tracks = [
    "Tiësto - Escape Me (feat. C.C. Sheffield)",
    "Miriana Conte - Kant",
    "Sw@da - Lusterka - Eurovision Version",
    "Ilona Mitrecey - Dans ma fusée",
    "Abor & Tynna - Baller",
    "Kodaline - Hell Froze Over",
    "Kodaline - Follow Your Fire",
    "Chi-Li - Новый год в постели",
    "Bobbi Arlo - POWERPLAY",
    "Red Sebastian - Strobe Lights",
    "Artemas - i like the way you kiss me",
    "Sw@da - Lusterka",
    "An-Marlen - külm",
    "Andrei Zevakin - ma ei tea sind",
    "AMORALU - Freedom",
    "Petunija - Į saldumą",
    "Katarsis - Tavo akys",
    "GØYA - After Storm",
    "Liepa Mondeikaite - Ar mylėtum?",
    "Scott Helman - PDA",
    "Tautumeitas - Bur man laimi",
    "Chi-Li - Сердце",
    "Vremya i Steklo - Тролль",
    "Vremya i Steklo - Е,Бой",
    "Chi-Li - Лето",
    "Chi-Li - Маки",
    "Chi-Li - Преступление",
    "TWIN XL - Try",
    "TWIN XL - Give It Up",
    "TWIN XL - Friends",
    "TWIN XL - Everybody's Talkin'",
    "Chad Tepper - NeverEnding Nightmare",
    "Shkodra Elektronike - Zjerm",
    "ALIKA - Bon Appetit",
    "Annalisa - Sinceramente",
    "Annalisa - Principessa (feat. Chadia Rodriguez)",
    "Mansionair - Guillotine",
    "The Wombats - Your Body Is a Weapon",
    "Therapie TAXI - Parallèle",
    "Merk & Kremont - Sad Story (Out Of Luck)",
    "Samanta Tina - The Moon Is Rising - Original",
    "Duck Sauce - It's You",
    "Love Fame Tragedy - Riding a Wave",
    "Austin Mahone - Till I Find You",
    "Alice Merton - Vertigo",
    "TWIN XL - Good",
    "KOYOTIE - Hello (Let's Go)",
    "Harlin James - So Glamorous",
    "Royal Republic - Stop Movin'",
    "Bambee - Bumble Bee"
]

response = requests.post(url, json={"tracks": tracks})

print("Status code:", response.status_code)
print("Response:")
try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Ошибка при декодировании JSON:", str(e))
    print("Raw text:", response.text)

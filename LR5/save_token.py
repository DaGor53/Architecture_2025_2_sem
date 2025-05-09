import requests
import time

time.sleep(60)

response = requests.post("http://registration_sys:8000/token", data={
    "username": "admin@mail.ru",
    "password": "admin"
})

print(response.status_code)
print(response.text)

if response.status_code == 200:
    token = response.json()["access_token"]
    with open("/shared/token.txt", "w") as f:
        f.write(token)
else:
    raise Exception("Failed to obtain token")
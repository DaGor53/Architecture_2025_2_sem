import requests, json, time
time.sleep(15)

for i in range(1,101):
    url = 'http://registration_sys:8000/users/'
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    user = dict()
    user['first_name']=f'Ivan{i}'
    user['last_name']=f'Ivanov{i}'
    user['email']=f'Ivanov{i}@mail.ru'
    user['password']=f'password{i}'
    user['role']=f'user'
    json_request = json.dumps(user, ensure_ascii=False).encode('utf-8')
    response = requests.post(url = url,headers=headers,data=json_request)
    if response.status_code != 200:
        print(response.status_code)
        break
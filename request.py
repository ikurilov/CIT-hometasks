import requests

api = 'https://cit-home1.herokuapp.com/api'

help_request = requests.get(api + '/help')

print(help_request.text)

headers_request = requests.get(api + '/headers')

print(headers_request.text)

register_data = {'first_name': 'Ilya', 'last_name': 'Kurilov'}

register_request = requests.post(api + '/register', json=register_data)

print(register_request.json()['answer'])

check_request = requests.get(api + '/check_me')

print(check_request.json())


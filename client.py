import requests
js = {"nickname": 'Alex'}
r = requests.post('http://localhost:8080/add_new_user', params=js)
print(r.text)
js = {"nickname": 'Andrew'}
r = requests.post('http://localhost:8080/add_new_user', params=js)
print(r.text)
r = requests.get('http://localhost:8080/users')
print(r.text)
js = {'client1': 'Alex', 'client2': 'Andrew'}
r = requests.post('http://localhost:8080/create_new_chat', params=js)
print(r.text)
js = {'chat_id': 1, 'client': 'Alex', 'message': 'Hello world'}
r = requests.post('http://localhost:8080/send_message', params=js)
print(r.text)
js = {'chat_id': 0, 'client': 'Andrew', 'message': 'Hello world'}
r = requests.post('http://localhost:8080/send_message', params=js)
print(r.text)
js = {"chat_id": 0, "client": 'Alex'}
r = requests.get('http://localhost:8080/get_messages', params=js)
print(r.text)



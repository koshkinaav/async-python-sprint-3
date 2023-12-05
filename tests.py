import requests
import unittest


class MyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("Run before all tests...")
        js_Alex = {"nickname": 'Alex'}
        r_Alex = requests.post('http://127.0.0.1:8080/add_new_user', params=js_Alex)
        js_Andrew = {"nickname": 'Andrew'}
        r_Andrew = requests.post('http://127.0.0.1:8080/add_new_user', params=js_Andrew)
        MyTest().assertEqual(r_Alex.text, 'User with nickname Alex added')
        MyTest().assertEqual(r_Andrew.text, 'User with nickname Andrew added')

    def test_get_users(self):
        r = requests.get('http://127.0.0.1:8080/users')
        self.assertEqual(r.text, 'Alex; Andrew')

    def test_create_new_chat(self):
        url = 'http://127.0.0.1:8080/create_new_chat'
        js = {
            'client_ids': ['client_id_1', 'client_id_2', 'client_id_3']  # Список client_ids
        }
        r = requests.post(url, params=js)
        self.assertEqual("Chat between ['client_id_1', 'client_id_2', 'client_id_3'] created. Id is 1", r.text)

    def test_send_message(self):
        js = {'chat_id': 1, 'client': 'Alex', 'message': 'Hello world'}
        r = requests.post('http://127.0.0.1:8080/send_message', params=js)
        self.assertEqual(r.text, "Message 'Hello world' from Alex added to chat 1")
        js = {'chat_id': 0, 'client': 'Andrew', 'message': 'Hello world'}
        r = requests.post('http://localhost:8080/send_message', params=js)
        self.assertEqual(r.text, "Message 'Hello world' from Andrew added to chat 0")

    @classmethod
    def tearDownClass(cls) -> None:
        print("Run after all tests...")
        js = {"chat_id": 0, "client": 'Andrew'}
        r = requests.get('http://127.0.0.1:8080/get_messages', params=js)
        MyTest().assertEqual(r.text, "[{'client_id': 'Andrew', 'message': 'Hello world'}]")

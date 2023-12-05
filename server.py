from chat_object import Chat
import asyncio
import logging
from urllib.parse import urlparse, parse_qs

logging.basicConfig(
    format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Server:

    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 8080
        self.clients = []  # полный список клиентов (nicknam'ов)
        self.chats = {}  # словарь чатов
        self.generator = self.id_generator()
        public_chat = Chat(id=next(self.generator))
        public_chat.clients = self.clients
        public_chat.messages = []
        self.chats[0] = public_chat

    @staticmethod
    def id_generator():
        '''
        Генератор для создания новых id чатов
        '''
        num = 0
        while True:
            yield num
            num += 1

    def get_method_path_params(self, request: bytes) -> tuple:

        headers = request.decode().split('\r\n')
        # Парсинг заголовков
        method, url, _ = headers[0].split(' ')
        headers = headers[1:]
        # Получаем путь и параметры из URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)
        return method, path, params

    def get_users(self) -> str:
        cl = '; '.join(self.clients)
        response = 'HTTP/1.1 200 OK\r\n\r\n' + cl
        logging.info('GET /users 200')
        return response

    def post_add_new_user(self, params: dict) -> str:
        nickname = params.get('nickname', [''])[0]
        if nickname:
            if nickname not in self.clients:
                self.clients.append(nickname)
                self.chats[0].clients = self.clients  # Добавляем пользователя в общий чат
                logging.info('POST /add_new_user 200')
                logging.info(f'User with nickname {nickname} added')
                response = f'HTTP/1.1 200 OK\r\n\r\nUser with nickname {nickname} added'
                return response

            else:
                logging.info('POST /add_new_user 400')
                response = 'HTTP/1.1 400 Already exists\r\n\r\nnickname {} aready exists'.format(nickname)
                return response

        else:
            logging.info('POST /add_new_user 400')
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing nickname parameter'
            return response

    def post_create_new_chat(self, params: dict) -> str:
        client_ids = params.get('client_ids')
        print(client_ids)
        try:
            if len(client_ids) < 2:
                logging.info('POST /create_new_chat 400')
                response = 'HTTP/1.1 400 Bad Request\r\n\r\nAt least two client_ids are required'
                return response
            else:
                new_chat_id = next(self.generator)
                new_chat = Chat(id=new_chat_id)
                new_chat.messages = []
                new_chat.clients = client_ids
                self.chats[new_chat_id] = new_chat
                logging.info('POST /create_new_chat 200')
                logging.info(f'Chat between {client_ids} created. Id is {new_chat_id}')
                response = f'HTTP/1.1 200 OK\r\n\r\nChat between {client_ids} created. Id is {new_chat_id}'
                return response
        except:
            logging.info('POST /create_new_chat 400')
            response = 'HTTP/1.1 400 Bad Request\r\n\r\n'
            return response

    def post_send_message(self, params: dict) -> str:
        chat_id = params.get('chat_id')[0]
        client = params.get('client', [''])[0]
        message = params.get('message', [''])[0]
        if chat_id and client and message:
            chat = self.chats[int(chat_id)]
            chat.send_message(client, message)
            logging.info('POST /send_message 200')
            logging.info(f"Message '{message}' from {client} added to chat {chat_id}")
            response = f"HTTP/1.1 200 OK\r\n\r\nMessage '{message}' from {client} added to chat {chat_id}"
            return response
        else:
            logging.info('POST /send_message 400')
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing chat_id or client or message parameters'
            return response

    def get_messages(self, params: dict) -> str:
        chat_id = params.get('chat_id')[0]
        client = params.get('client', [''])[0]
        if chat_id and client:
            if client in self.chats[int(chat_id)].clients:
                chat = self.chats[int(chat_id)]
                messages = chat.messages[-20:]
                logging.info('GET /get_messages 200')
                response = f"HTTP/1.1 200 OK\r\n\r\n{messages}"
                return response

            else:
                logging.info('GET /get_messages 400')
                response = f'HTTP/1.1 400 Bad Request\r\n\r\nClient {client} not found in chat {chat_id}'
                return response

        else:
            logging.info('GET /get_messages 400')
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing chat_id or client parameters'
            return response

    async def handle_request(self, reader: asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter) -> None:
        request = await reader.readline()
        method, path, params = self.get_method_path_params(request)
        if method == 'GET' and path == '/users':
            response = self.get_users()
        elif method == 'POST' and path == '/add_new_user':
            response = self.post_add_new_user(params)
        elif method == 'POST' and path == '/create_new_chat':
            response = self.post_create_new_chat(params)
        elif method == 'POST' and path == '/send_message':
            response = self.post_send_message(params)
        elif method == 'GET' and path == '/get_messages':
            response = self.get_messages(params)
        writer.write(response.encode())
        await writer.drain()
        writer.close()

    async def start_server(self) -> None:
        server_object = await asyncio.start_server(
            self.handle_request, self.ip, self.port)

        addr = server_object.sockets[0].getsockname()
        logging.info(f'Serving on {addr}')

        async with server_object:
            await server_object.serve_forever()


server = Server()

asyncio.run(server.start_server())

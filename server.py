import asyncio
from urllib.parse import urlparse, parse_qs
from chat_object import Chat
import logging
logging.basicConfig(
    format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
clients = []  # полный список клиентов (nicknam'ов)
chats = {}  # словарь чатов
groups = []  # список кортежей nicknam'ов участников private чатов


# http://localhost:8080/create_new_chat?client1=Alex&client2=Andrew

def id_generator():
    '''
    Генератор для создания новых id чатов
    '''
    num = 0
    while True:
        yield num
        num += 1


# Инициализируем общий чат
generator = id_generator()
public_chat = Chat(id=next(generator))
public_chat.clients = clients
public_chat.messages = []
chats[0] = public_chat


async def handle_request(reader, writer):
    request = await reader.readline()
    headers = request.decode().split('\r\n')
    # Парсинг заголовков
    method, url, protocol = headers[0].split(' ')
    headers = headers[1:]

    # Получаем путь и параметры из URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    params = parse_qs(parsed_url.query)

    # Обработка запроса
    if method == 'GET' and path == '/users':
        # получить всех пользователей
        cl = '; '.join(clients)
        response = f'HTTP/1.1 200 OK\r\n\r\n' + cl
        logging.warning('GET /users 200')
    elif method == 'POST' and path == '/add_new_user':
        # метод добавляет нового пользователя с nickname, указанным в теле запроса (дубли невозможны)
        nickname = params.get('nickname', [''])[0]
        if nickname:
            if nickname not in clients:
                clients.append(nickname)
                chats[0].clients = clients  # Добавляем пользователя в общий чат
                response = f'HTTP/1.1 200 OK\r\n\r\nUser with nickname {nickname} added'
                logging.warning('POST /add_new_user 200')
                logging.info(f'User with nickname {nickname} added')

            else:
                response = 'HTTP/1.1 400 Already exists\r\n\r\nnickname {} aready exists'.format(nickname)
                logging.warning('POST /add_new_user 400')
        else:
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing nickname parameter'
            logging.warning('POST /add_new_user 400')

    elif method == 'POST' and path == '/create_new_chat':
        # метод создает private чат между пользователями
        client_id_1 = params.get('client1', [''])[0]
        client_id_2 = params.get('client2', [''])[0]
        if client_id_1 and client_id_2:
            if (client_id_1, client_id_2) in groups:
                response = (f'HTTP/1.1 400 Already exists\r\n\r\nChat between {client_id_1} and {client_id_2} already '
                            f'exists')
                logging.warning('POST /create_new_chat 400')
            elif client_id_1 not in clients:
                response = f'HTTP/1.1 400 Not found\r\n\r\nUser {client_id_1} not found'
                logging.warning('POST /create_new_chat 400')
            elif client_id_2 not in clients:
                response = f'HTTP/1.1 400 Not found\r\n\r\nUser {client_id_2} not found'
                logging.warning('POST /create_new_chat 400')
            else:
                id = next(generator)
                new_chat = Chat(id=id)
                new_chat.messages = []
                new_chat.clients = [client_id_1, client_id_2]
                chats[id] = new_chat
                response = f'HTTP/1.1 200 OK\r\n\r\nChat between {client_id_1} and {client_id_2} created. Id is {id}'
                logging.warning('POST /create_new_chat 200')
                logging.warning(f'Chat between {client_id_1} and {client_id_2} created. Id is {id}')
        else:
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing client_1 or client_2 parameters'
            logging.warning('POST /create_new_chat 400')

    elif method == 'POST' and path == '/send_message':
        chat_id = params.get('chat_id', [''])[0]
        client = params.get('client', [''])[0]
        message = params.get('message', [''])[0]
        if chat_id and client and message:
            chat = chats[int(chat_id)]
            chat.send_message(client, message)
            response = f"HTTP/1.1 200 OK\r\n\r\nMessage '{message}' from {client} added to chat {chat_id}"
            logging.warning('POST /send_message 200')
            logging.warning(f"Message '{message}' from {client} added to chat {chat_id}")
        else:
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing chat_id or client or message parameters'
            logging.warning('POST /send_message 400')

    elif method == 'GET' and path == '/get_messages':
        chat_id = params.get('chat_id', [''])[0]
        client = params.get('client', [''])[0]
        if chat_id and client:
            if client in chats[int(chat_id)].clients:
                chat = chats[int(chat_id)]
                messages = chat.messages[-20:]
                response = f"HTTP/1.1 200 OK\r\n\r\n{messages}"
                logging.warning('GET /get_messages 200')
            else:
                response = f'HTTP/1.1 400 Bad Request\r\n\r\nClient {client} not found in chat {chat_id}'
                logging.warning('GET /get_messages 400')
        else:
            response = 'HTTP/1.1 400 Bad Request\r\n\r\nMissing chat_id or client parameters'
            logging.warning('GET /get_messages 400')

    writer.write(response.encode())
    await writer.drain()
    writer.close()


async def start_server():
    server = await asyncio.start_server(
        handle_request, 'localhost', 8080)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


asyncio.run(start_server())

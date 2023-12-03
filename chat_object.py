from async_class import AsyncClass


class Chat(AsyncClass):

    async def __ainit__(self, chat_id: int):
        self.chat_id = chat_id
        self.clients = []
        self.messages = []

    async def add_client_to_chat(self, client_id: int):
        self.clients.append(client_id)

    def send_message(self, client_id: int, message: str):
        self.messages.append({'client_id': client_id, 'message': message})

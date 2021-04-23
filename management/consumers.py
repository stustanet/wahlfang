import json

from channels.generic.websocket import AsyncWebsocketConsumer


class CastVotesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group = "Election-" + self.scope['url_route']['kwargs']['pk']  # pylint: disable=W0201
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def send_reload(self, event):
        await self.send(text_data=json.dumps({
            'reload': True,
        }))

import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from vote.models import Session


class VoteConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group = await database_sync_to_async(self.get_session_key)()  # pylint: disable=W0201
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def send_reload(self, event):
        await self.send(text_data=json.dumps({
            'reload': event['id'],
        }))

    def get_session_key(self):
        if 'uuid' in self.scope['url_route']['kwargs']:
            uuid = self.scope['url_route']['kwargs']['uuid']
            session = Session.objects.get(spectator_token=uuid)
        else:
            session = self.scope['user'].session
        return "Session-" + str(session.pk)

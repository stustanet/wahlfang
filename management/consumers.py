import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ElectionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group = "Election-" + self.scope['url_route']['kwargs']['pk']  # pylint: disable=W0201
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def send_reload(self, event):
        await self.send(text_data=json.dumps({
            'reload': event['id'],
        }))


class SessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        session = self.scope['url_route']['kwargs']['pk']
        # reload if a new voter logged in, or if a election of the session was changed (like added)
        self.groups = ["Login-Session-" + session, "Session-" + session,
                       "SessionAlert-" + session]  # pylint: disable=W0201
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def send_reload(self, event):
        await self.send(text_data=json.dumps({
            'reload': event['id'],
        }))

    async def send_alert(self, event):
        await self.send(text_data=json.dumps({
            'alert': {'title': event.get('title', 'Alert'), 'msg': event['msg'], 'reload': event.get('reload')},
        }))

    async def send_succ(self, event):
        await self.send(text_data=json.dumps({
            'succ': event['msg'],
        }))

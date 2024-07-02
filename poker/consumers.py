import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PokerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["session_public_identifier"]
        self.room_name = "RoomName"
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        messageType = text_data_json.get("type", None)
        content = text_data_json.get("content", None)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": messageType,
                "content": content
            }
        )

    async def participant_update(self, event):
        messageType = event.get("type", None)
        content = event.get("content", None)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": messageType,
            "content": content
        }))

    async def participant_needACoffee(self, event):
        messageType = event.get("type", None)
        content = event.get("content", None)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": messageType,
            "content": content
        }))

    async def organizer_isEstimationRunningChanged(self, event):
        messageType = event.get("type", None)
        content = event.get("content", None)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": messageType,
            "content": content
        }))

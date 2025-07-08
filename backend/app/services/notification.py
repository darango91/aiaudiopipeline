import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

import redis.asyncio as redis
from fastapi import WebSocket

from app.core.config import settings
from app.schemas.notification import NotificationType, Notification

logger = logging.getLogger(__name__)

# Dictionary to store active WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

class NotificationService:
    """
    Service for sending real-time notifications to connected clients.
    """
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._redis_client = None
    
    @property
    async def redis_client(self):
        """
        Lazy initialization of Redis client.
        """
        if self._redis_client is None:
            self._redis_client = redis.from_url(str(self.redis_url))
        return self._redis_client
    
    async def send_notification(
        self, 
        session_id: str, 
        notification_type: NotificationType, 
        payload: Dict[str, Any]
    ) -> None:
        """
        Send a notification to clients connected to a specific session.
        
        Args:
            session_id: The session ID to send the notification to
            notification_type: Type of notification
            payload: Notification payload
        """
        try:
            notification = Notification(
                type=notification_type,
                session_id=session_id,
                timestamp=datetime.now(datetime.timezone.utc),
                payload=payload
            )
            
            redis_client = await self.redis_client
            await redis_client.publish(
                f"notifications:{session_id}",
                json.dumps(notification.model_dump(), cls=DateTimeEncoder)
            )
            
            try:
                await self.broadcast_notification(notification)
            except Exception as e:
                logger.error(f"Error broadcasting notification via WebSocket: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    async def subscribe_to_notifications(self, session_id: str, callback):
        """
        Subscribe to notifications for a specific session.
        
        Args:
            session_id: The session ID to subscribe to
            callback: Callback function to call when a notification is received
        """
        client = await self.redis_client
        pubsub = client.pubsub()
        await pubsub.subscribe(f"notifications:{session_id}")
        
        asyncio.create_task(self._process_messages(pubsub, callback))
        
    async def broadcast_notification(self, notification: Notification):
        """
        Broadcast a notification to all connected clients for a specific session.
        
        Args:
            notification: The notification to broadcast
        """
        session_id = notification.session_id
        logger.info(f"Broadcasting notification of type {notification.type} to session {session_id}")
        
        if session_id in active_connections:
            connections_to_remove = []
            
            for connection in active_connections[session_id]:
                try:
                    message = {
                        "type": notification.type,
                        "session_id": session_id,
                        "timestamp": notification.timestamp.isoformat(),
                        "payload": notification.payload
                    }
                    
                    json_str = json.dumps(message, cls=DateTimeEncoder)
                    logger.debug(f"Sending notification: {json_str}")
                    await connection.send_text(json_str)
                except Exception as e:
                    logger.error(f"Error sending notification to client: {e}")
                    connections_to_remove.append(connection)
            
            for connection in connections_to_remove:
                if connection in active_connections[session_id]:
                    active_connections[session_id].remove(connection)
        
    async def _process_messages(self, pubsub, callback):
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    try:
                        notification = json.loads(message["data"])
                        await callback(notification)
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON in notification message")
                    except Exception as e:
                        logger.error(f"Error processing notification: {str(e)}")
                
                await asyncio.sleep(0.01)
        
        except Exception as e:
            logger.error(f"Error in notification subscription: {str(e)}")
        finally:
            try:
                await pubsub.unsubscribe()
            except Exception as e:
                logger.error(f"Error unsubscribing from pubsub: {str(e)}")
                pass

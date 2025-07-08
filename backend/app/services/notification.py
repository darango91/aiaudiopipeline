import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

# Custom JSON encoder for datetime objects
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
            # Create notification object using the Notification class
            notification = Notification(
                type=notification_type,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                payload=payload
            )
            
            # Publish to Redis channel for the session
            redis_client = await self.redis_client
            await redis_client.publish(
                f"notifications:{session_id}",
                json.dumps(notification.model_dump(), cls=DateTimeEncoder)
            )
            
            # Also broadcast directly to connected WebSocket clients
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
        
        # Process messages in background task
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
                    # Format the notification in a way the frontend expects
                    message = {
                        "type": notification.type,
                        "session_id": session_id,
                        "timestamp": notification.timestamp.isoformat(),
                        "payload": notification.payload
                    }
                    
                    # Convert to JSON string and send
                    json_str = json.dumps(message, cls=DateTimeEncoder)
                    logger.debug(f"Sending notification: {json_str}")
                    await connection.send_text(json_str)
                except Exception as e:
                    logger.error(f"Error sending notification to client: {e}")
                    # Mark connection for removal
                    connections_to_remove.append(connection)
            
            # Remove failed connections after iteration
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
                
                # Small sleep to avoid CPU spinning
                await asyncio.sleep(0.01)
        
        except Exception as e:
            logger.error(f"Error in notification subscription: {str(e)}")
        finally:
            # Ensure we unsubscribe
            try:
                await pubsub.unsubscribe()
            except Exception as e:
                logger.error(f"Error unsubscribing from pubsub: {str(e)}")
                pass

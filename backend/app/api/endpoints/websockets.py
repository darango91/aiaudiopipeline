import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.notification import Notification, NotificationType
from app.services.notification import NotificationService, active_connections

router = APIRouter()
notification_service = NotificationService()


@router.websocket("/connect/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    client_id: str = Query(None),
):
    """
    WebSocket endpoint for real-time communication.
    """
    await websocket.accept()
    
    # Register the connection
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "client_id": client_id or "anonymous",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Listen for incoming messages from the client
        while True:
            try:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    # Process the message based on its type
                    if message.get("type") == "audio_chunk":
                        # Handle audio chunk (this would typically be done via REST API)
                        pass
                    elif message.get("type") == "client_event":
                        # Handle client events
                        pass
                    elif message.get("type") == "ping":
                        # Respond to ping with pong
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
            except Exception as e:
                # Log the error but don't break the loop
                logger.error(f"Error processing WebSocket message: {str(e)}")
                # Only break if it's a disconnect error
                if isinstance(e, WebSocketDisconnect):
                    raise
    except WebSocketDisconnect:
        # Remove the connection when client disconnects
        active_connections[session_id].remove(websocket)
        if not active_connections[session_id]:
            del active_connections[session_id]
    except Exception as e:
        # Handle other exceptions
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
        except:
            pass
        
        # Clean up connection
        if session_id in active_connections and websocket in active_connections[session_id]:
            active_connections[session_id].remove(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]


@router.websocket("/audio-stream/{session_id}")
async def audio_stream_endpoint(
    websocket: WebSocket,
    session_id: str,
):
    """
    WebSocket endpoint for streaming audio data.
    """
    await websocket.accept()
    
    try:
        # Process incoming audio stream
        while True:
            # Receive binary audio data
            audio_data = await websocket.receive_bytes()
            
            # Process the audio data (this would be handled by the audio processor service)
            # This is a placeholder - actual implementation would process the audio
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "audio_received",
                "bytes_received": len(audio_data)
            })
    except WebSocketDisconnect:
        # Handle disconnection
        pass
    except Exception as e:
        # Handle other exceptions
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
        except:
            pass


# Function to broadcast notifications to connected clients
async def broadcast_notification(notification: Notification):
    """
    Broadcast a notification to all connected clients for a specific session.
    """
    await notification_service.broadcast_notification(notification)

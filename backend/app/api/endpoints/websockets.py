import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.schemas.notification import Notification
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
    
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)
    
    try:
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "client_id": client_id or "anonymous",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    if message.get("type") == "audio_chunk":
                        pass
                    elif message.get("type") == "client_event":
                        pass
                    elif message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                if isinstance(e, WebSocketDisconnect):
                    raise
    except WebSocketDisconnect:
        active_connections[session_id].remove(websocket)
        if not active_connections[session_id]:
            del active_connections[session_id]
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
        except:
            pass
        
        if session_id in active_connections and websocket in active_connections[session_id]:
            active_connections[session_id].remove(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]


@router.websocket("/audio-stream/{session_id}")
async def audio_stream_endpoint(
    websocket: WebSocket,
):
    """
    WebSocket endpoint for streaming audio data.
    """
    await websocket.accept()
    
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            
            await websocket.send_json({
                "type": "audio_received",
                "bytes_received": len(audio_data)
            })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
        except:
            pass


async def broadcast_notification(notification: Notification):
    """
    Broadcast a notification to all connected clients for a specific session.
    """
    await notification_service.broadcast_notification(notification)

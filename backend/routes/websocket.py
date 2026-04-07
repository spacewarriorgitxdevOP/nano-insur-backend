"""
P1 - WebSocket Handler
Real-time status updates pushed to P2's React Native app.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """
    Manages all active WebSocket connections.
    Broadcasts claim status updates to all connected mobile clients.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        count = len(self.active_connections)
        logger.info(f"🔌 WebSocket connected. Total: {count}")
        print(f"🔌 WebSocket connected. Total clients: {count}")
        
        # Send welcome message
        await websocket.send_json({
            "event": "connected",
            "data": {
                "message": "Connected to InsureClaim real-time updates",
                "active_clients": count
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    async def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket"""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        count = len(self.active_connections)
        logger.info(f"🔌 WebSocket disconnected. Total: {count}")
        print(f"🔌 WebSocket disconnected. Total clients: {count}")

    async def broadcast(self, message: dict):
        """
        Broadcast a message to ALL connected clients.
        This is called from REST routes when claim status changes.
        """
        if not self.active_connections:
            return
        
        message["timestamp"] = datetime.utcnow().isoformat()
        
        disconnected = []
        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected.append(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            await self.disconnect(conn)
        
        if self.active_connections:
            logger.info(
                f"📡 Broadcast '{message.get('event')}' to "
                f"{len(self.active_connections)} clients"
            )

    async def send_to_client(self, websocket: WebSocket, message: dict):
        """Send a message to a specific client"""
        try:
            message["timestamp"] = datetime.utcnow().isoformat()
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send to specific client: {e}")
            await self.disconnect(websocket)


# ─── Singleton Manager ────────────────────────────────
manager = ConnectionManager()


# ─── WebSocket Endpoint ───────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time claim updates.
    
    P2's React Native app connects here.
    Receives: heartbeat pings from client
    Sends: claim status updates, new claims, OCR results
    
    Message format:
    {
        "event": "status_update" | "new_claim" | "ocr_complete" | "heartbeat",
        "data": { ... },
        "timestamp": "2024-01-15T10:30:00.000Z"
    }
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client (heartbeat/ping)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                event = message.get("event", "unknown")
                
                if event == "ping":
                    # Respond to heartbeat
                    await manager.send_to_client(websocket, {
                        "event": "pong",
                        "data": {"status": "alive"}
                    })
                
                elif event == "subscribe":
                    # Client wants to subscribe to specific claim updates
                    claim_id = message.get("data", {}).get("claim_id")
                    await manager.send_to_client(websocket, {
                        "event": "subscribed",
                        "data": {"claim_id": claim_id}
                    })
                
                else:
                    # Echo unknown events
                    await manager.send_to_client(websocket, {
                        "event": "echo",
                        "data": message
                    })
                    
            except json.JSONDecodeError:
                await manager.send_to_client(websocket, {
                    "event": "error",
                    "data": {"message": "Invalid JSON"}
                })
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


# ─── Health check for WebSocket ───────────────────────

@router.get("/ws/status", tags=["WebSocket"])
async def websocket_status():
    """Check WebSocket server status and connected clients count"""
    return {
        "status": "running",
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }
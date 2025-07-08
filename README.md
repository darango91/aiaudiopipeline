# AI Audio Assistant

A real-time audio processing system that transcribes speech, detects keywords, and provides contextual talking points during prospect calls. This system leverages modern cloud APIs and microservices architecture to deliver accurate transcription with real-time feedback.

## Features

- **Real-time Audio Processing**: Transcribe speech from file uploads or streaming audio using OpenAI's Whisper API
- **Keyword Detection**: Identify important keywords in conversations with configurable detection rules
- **Contextual Talking Points**: Provide relevant information when keywords are detected to enhance conversation quality
- **Real-time Notifications**: Push updates to clients via WebSocket with robust error handling
- **User-friendly Interface**: Clean React frontend with real-time transcript display
- **Docker Containerization**: Easy deployment with Docker and Docker Compose

## Architecture

The system is built with a clean, modular architecture using containerization:

- **Backend**: Python 3.10+ with FastAPI for REST and WebSocket APIs
- **Frontend**: React with Vite and Tailwind CSS
- **Database**: PostgreSQL for storing keywords, talking points, transcripts, and sessions
- **Message Broker**: Redis for queue-based processing and pub/sub notifications
- **Reverse Proxy**: Nginx for routing API, WebSocket, and frontend requests
- **Containerization**: Docker and Docker Compose for easy deployment and scaling
- **API Integration**: OpenAI Whisper API (v1.0.0+) for high-quality speech transcription

### System Components

- **API Endpoints**: 
  - `/audio/sessions`: Create and manage audio transcription sessions
  - `/audio/upload`: Handle audio file uploads for transcription
  - `/keywords`: Manage keyword detection rules
  - `/ws/connect/{session_id}`: WebSocket endpoint for real-time updates

- **Services**:
  - **TranscriptionService**: Integrates with OpenAI Whisper API with fallback mechanisms
  - **NotificationService**: Manages real-time WebSocket notifications with Redis pub/sub
  - **KeywordDetector**: Identifies keywords in transcripts using pattern matching
  - **AudioProcessor**: Orchestrates the audio processing workflow

- **Data Flow**:
  1. Audio is uploaded or streamed to the backend
  2. Audio is processed by the TranscriptionService
  3. Transcripts are analyzed for keywords
  4. Real-time notifications are sent to connected clients
  5. Frontend displays transcripts and talking points

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (for Whisper transcription)

### Installation & Setup

1. Clone the repository
2. Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=aiaudio
   POSTGRES_HOST=db
   REDIS_HOST=redis
   AUDIO_STORAGE_PATH=/app/audio_storage
   VITE_API_URL=http://localhost:8000
   ```

   Note: The `.env.example` file provides a template for the required environment variables.
4. Build and start the containers:
   ```
   docker compose build
   docker compose up -d
   ```

This will start all required services in Docker containers.

### Accessing the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000
- **Nginx Gateway**: http://localhost:8080

## Development

### Project Structure

```
aiaudiopipeline/
├── backend/                # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   ├── endpoints/  # Route handlers
│   │   │   └── router.py   # API router configuration
│   │   ├── core/           # Core configuration
│   │   │   └── config.py   # Environment and app settings
│   │   ├── crud/           # Database CRUD operations
│   │   ├── db/             # Database session management
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── audio.py    # Audio and transcription schemas
│   │   │   └── notification.py # Notification schemas
│   │   └── services/       # Business logic services
│   │       ├── audio_processor.py # Audio processing service
│   │       ├── transcription.py # OpenAI integration
│   │       ├── keyword_detector.py # Keyword detection
│   │       └── notification.py # WebSocket notifications
│   ├── scripts/            # Utility scripts
│   ├── tests/              # Backend tests
│   └── alembic/            # Database migrations
├── frontend/               # React frontend
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API and WebSocket services
│   │   └── styles/         # CSS styles
│   └── package.json        # Frontend dependencies
├── docker/                 # Docker configuration
│   ├── backend/            # Backend Dockerfile
│   ├── frontend/           # Frontend Dockerfile
│   └── nginx/              # Nginx configuration
├── .env                    # Environment variables
├── .env.example           # Example environment variables
└── docker-compose.yml      # Docker Compose configuration
```

### Backend Development

The backend is built with FastAPI and follows a clean architecture with separation of concerns:

- **API Endpoints**: Handle HTTP requests and WebSocket connections
- **Services**: Implement business logic with error handling and fallbacks
- **Models**: Define database schema using SQLAlchemy ORM
- **Schemas**: Define data validation and serialization using Pydantic
- **Schemas**: Validate request/response data using Pydantic v2.11+

## Technical Implementation Details

### OpenAI API Integration

The system integrates with OpenAI's Whisper API for high-quality speech transcription:

- Uses the latest OpenAI Python SDK (v1.0.0+)
- Handles response format changes between API versions
- Implements fallback mechanisms for API quota limitations
- Supports both file-based and streaming audio transcription

```python
# Example of OpenAI API integration with error handling
async def transcribe_file(self, file_path: str) -> TranscriptionResult:
    if not self.api_key:
        raise ValueError("OpenAI API key is not configured")
        
    try:                
        with open(file_path, "rb") as audio_file:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    temperature=0.0,
                    language="en"
                )
            )
        # Process response...
    except Exception as e:
        logger.error(f"Error transcribing audio file: {str(e)}")
        raise
```

### Real-time Notifications

The system uses a combination of Redis pub/sub and WebSockets for real-time notifications:

- WebSocket connections are managed per session
- Redis pub/sub enables scaling across multiple backend instances
- Custom JSON serialization handles complex data types (like datetime)
- Robust error handling ensures notifications are delivered reliably

```python
# Example of notification broadcasting with proper serialization
async def broadcast_notification(self, notification: Notification):
    try:
        # Serialize with custom encoder for datetime objects
        notification_json = json.dumps(notification.model_dump(), cls=DateTimeEncoder)
        
        # Send to all connected WebSocket clients
        for connection in self.active_connections.get(notification.session_id, []):
            await connection.send_text(notification_json)
    except Exception as e:
        logger.error(f"Error broadcasting notification: {e}")
```

### Containerization and Deployment

The application is fully containerized using Docker and Docker Compose:

- Separate containers for backend, frontend, database, Redis, and Nginx
- Environment variables for configuration across services
- Volume mounts for persistent data storage
- Network configuration for inter-service communication

## Recent Improvements and Fixes

### API Compatibility Updates

- Updated OpenAI client usage to be compatible with SDK v1.0.0+
- Fixed response handling to work with object attributes instead of dictionary access
- Removed mock transcription fallback for cleaner implementation
- Added proper error handling for API responses

### WebSocket Notification Fixes

- Fixed notification broadcasting with proper WebSocket connection management
- Implemented custom JSON serialization for datetime objects
- Changed WebSocket sending from `send_json()` to `send_text()` with pre-serialized JSON
- Added proper error handling for WebSocket connections

### Environment Variable Management

- Centralized environment variable configuration in `.env` file
- Ensured proper environment variable propagation to Docker containers
- Added validation for required environment variables
- Fixed timezone import issue in datetime handling

## Future Enhancements

- Implement more sophisticated keyword detection with NLP techniques
- Add user authentication and multi-tenant support
- Implement speaker diarization
- Implement real-time audio streaming from browser
- Add analytics dashboard for call insights
- Implement error recovery mechanisms for API failures
- Add support for additional languages and audio formats

### Frontend Development

The frontend is a React application that demonstrates the capabilities of the backend:

- **Dashboard**: Main interface for audio recording and transcription
- **KeywordConfig**: Interface for managing keywords and talking points
- **Components**: Reusable UI components
- **Services**: API and WebSocket clients

## Testing

Run backend tests:

```bash
docker-compose exec backend pytest
```

## Deployment

The application is containerized and can be deployed to any environment that supports Docker:

1. Build the Docker images:
   ```
   docker-compose build
   ```

2. Start the services:
   ```
   docker-compose up -d
   ```

## Future Enhancements

- Implement authentication and authorization
- Enhance keyword detection with NLP techniques
- Implement speaker diarization
- Add analytics dashboard
- Implement real-time audio visualization
- Use S3 for audio storage

## License

This project is licensed under the MIT License - see the LICENSE file for details.

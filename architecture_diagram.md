# AI Audio Pipeline Architecture

```mermaid
graph TD
    %% Client Components
    Client[Client Browser]
    
    %% Frontend Components
    subgraph "Frontend (React)"
        UI[User Interface]
        APIClient[API Client]
        WSClient[WebSocket Client]
    end
    
    %% Nginx Layer
    subgraph "Nginx"
        Proxy[Reverse Proxy]
    end
    
    %% Backend Components
    subgraph "Backend (FastAPI)"
        API[REST API]
        WS[WebSocket Server]
        
        subgraph "Services"
            AudioProc[Audio Processor]
            TransService[Transcription Service]
            KeywordService[Keyword Detector]
            NotifService[Notification Service]
        end
        
        subgraph "Data Layer"
            Models[SQLAlchemy Models]
            Schemas[Pydantic Schemas]
            CRUD[CRUD Operations]
        end
    end
    
    %% External Services
    subgraph "External Services"
        OpenAI[OpenAI Whisper API]
    end
    
    %% Data Storage
    subgraph "Data Storage"
        Postgres[(PostgreSQL)]
        Redis[(Redis)]
        FileStorage[File Storage]
    end
    
    %% Flow Connections
    Client --> Proxy
    Proxy --> UI
    Proxy --> API
    Proxy --> WS
    
    UI --> APIClient
    UI --> WSClient
    APIClient --> Proxy
    WSClient --> Proxy
    
    API --> AudioProc
    API --> KeywordService
    WS --> NotifService
    
    AudioProc --> TransService
    AudioProc --> KeywordService
    AudioProc --> NotifService
    
    TransService --> OpenAI
    
    AudioProc --> Models
    KeywordService --> Models
    NotifService --> Redis
    
    Models --> CRUD
    CRUD --> Postgres
    
    AudioProc --> FileStorage
    
    %% Data Flow
    classDef frontend fill:#f9f,stroke:#333,stroke-width:2px
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px
    classDef storage fill:#bfb,stroke:#333,stroke-width:2px
    classDef external fill:#fbb,stroke:#333,stroke-width:2px
    
    class Client,UI,APIClient,WSClient frontend
    class API,WS,AudioProc,TransService,KeywordService,NotifService,Models,Schemas,CRUD backend
    class Postgres,Redis,FileStorage storage
    class OpenAI external
```

## Architecture Description

The AI Audio Pipeline is built with a modern microservices architecture that enables real-time audio processing and transcription. Here's a breakdown of the key components:

### Client Layer
- **Client Browser**: End-user interface for uploading audio files and viewing transcriptions

### Frontend Layer
- **React UI**: User interface built with React and styled with modern CSS
- **API Client**: Handles HTTP requests to the backend API
- **WebSocket Client**: Manages real-time communication with the backend

### Nginx Layer
- **Reverse Proxy**: Routes requests to appropriate services and handles load balancing

### Backend Layer
- **REST API**: FastAPI endpoints for handling HTTP requests
- **WebSocket Server**: Manages real-time connections with clients
- **Services**:
  - **Audio Processor**: Orchestrates the audio processing workflow
  - **Transcription Service**: Integrates with OpenAI Whisper API
  - **Keyword Detector**: Identifies keywords in transcripts
  - **Notification Service**: Manages WebSocket notifications
- **Data Layer**:
  - **SQLAlchemy Models**: ORM models for database entities
  - **Pydantic Schemas**: Data validation and serialization
  - **CRUD Operations**: Database access patterns

### External Services
- **OpenAI Whisper API**: Provides high-quality speech-to-text transcription

### Data Storage
- **PostgreSQL**: Stores structured data (sessions, transcripts, keywords)
- **Redis**: Handles pub/sub for real-time notifications
- **File Storage**: Stores uploaded audio files

## Data Flow

1. Client uploads audio file through the UI
2. Request passes through Nginx to the Backend API
3. Audio Processor saves the file and sends it to the Transcription Service
4. Transcription Service calls OpenAI Whisper API
5. Results are processed by the Keyword Detector
6. Notification Service sends real-time updates via WebSockets
7. UI displays transcription and keyword matches in real-time

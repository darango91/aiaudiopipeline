# AI Audio Assistant Frontend

This is the frontend application for the AI Audio Assistant, which provides a user interface for real-time audio transcription, keyword detection, and talking points notification.

## Features

- Real-time audio recording and streaming
- Live transcription display with speaker identification
- Keyword highlighting in transcripts
- Talking points notifications based on detected keywords
- Configuration interface for keywords and talking points

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- React Router
- Axios for API requests
- WebSocket for real-time communication

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Development

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

This will start the development server at http://localhost:3000.

### Building for Production

```bash
npm run build
```

This will generate optimized production files in the `dist` directory.

### Docker

This application is designed to be run in Docker as part of the full AI Audio Assistant stack. See the root `docker-compose.yml` file for details.

## Project Structure

- `src/components/` - React components
- `src/services/` - API and WebSocket services
- `src/styles/` - CSS styles

## Key Components

- `Dashboard.jsx` - Main interface for audio recording and transcription
- `AudioRecorder.jsx` - Audio recording controls and visualization
- `TranscriptDisplay.jsx` - Real-time transcript display with keyword highlighting
- `TalkingPointsPanel.jsx` - Display for detected keywords and talking points
- `KeywordConfig.jsx` - Interface for managing keywords and talking points

## Services

- `api.js` - REST API client for backend communication
- `websocket.js` - WebSocket client for real-time updates

## Environment Variables

The frontend expects the backend API to be available at `/api` and WebSocket at `/ws`. In development, these paths should be proxied to the appropriate backend services.

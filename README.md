# File Processing System with PII Detection

A microservices-based system that handles file uploads and automatically classifies/detects PII (Personally Identifiable Information) in documents.

## Components

- **Upload Service** (NestJS): Handles file uploads and inventory management
- **Classifier Service** (Python): Processes files and detects PII information

## Features

- File upload and management via MinIO
- Asynchronous file processing using Kafka
- PII detection and classification using Presidio
- MongoDB storage for file metadata and results

## Prerequisites

- Docker and Docker Compose
- Node.js and Nest.js
- Python 3.8
- MongoDB
- Apache Kafka

## Environment Setup

1. Copy the example environment files and configure them:
   ```bash
   cd classifier && cp .env.example .env
   cd upload && cp .env.example .env
   ```

2. Configure the following services in your .env files:
   - MongoDB connection
   - Kafka broker settings
   - API configurations

## Running the System

```bash
docker compose up -d
```

This will start the required infrastructure.

Start Upload Service:
```bash
cd upload
npm install
npm run start
```

Start Classifier Service:
```bash
cd classifier
pip install -r requirements.txt
python -m src.main
```

## API Endpoints

- `POST /upload`: Upload a new file
- `GET /files`: List all processed files
- `GET /files/:id`: Get specific file details

## Architecture

```
Upload Service → Kafka → Classifier Service
         ↓                        ↓
      MongoDB ←------------------ ✓
```

The system uses event-driven architecture where files are processed asynchronously through Kafka messaging.

## Database Schema

The system uses MongoDB with two main collections:

### FileInventory Collection
```typescript
{
  fileId: string,      // Unique identifier
  fileName: string,    // Original file name
  fileType: string,    // File extension/type
  fileLocation: string,// File storage path
  status: string,      // File status: "REQ"|"UPLOADED"|"DONE"|"ERROR"
  errorReason: string  // Error message if status is "ERROR"
}
```

### DataScanResult Collection
```typescript
{
  fileId: string,      // Reference to FileInventory
  results: [           // Array of PII findings
    {
      piiType: string,   // Type of PII found (e.g., "Email", "Phone")
      piiValue: string,  // The detected PII value
      location: string   // Location in file (e.g., "row: 3, column: Email")
    }
  ],
  createdAt: Date,    // Creation timestamp
  updatedAt: Date     // Last update timestamp
}
```

# TODO
- [ ] Add scripts for easy setup/build and teardown
- [ ] Add unit testing
- [ ] Add integration testing
- [ ] Add file validation module
- [ ] Add support for different PII detection models

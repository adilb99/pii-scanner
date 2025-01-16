import os
from dotenv import load_dotenv
from multiprocessing import cpu_count

load_dotenv()

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'file-uploads')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'file-classifier')
    
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB = os.getenv('MONGODB_DB', 'fileupload')
    
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', '../upload/uploads') 
    
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "uploads")
    
    # Kafka retry configuration
    KAFKA_MAX_RETRIES = int(os.getenv('KAFKA_MAX_RETRIES', '3'))
    KAFKA_RETRY_INTERVAL = int(os.getenv('KAFKA_RETRY_INTERVAL', '5'))  # seconds
    
    # Worker configuration
    WORKER_PROCESSES = int(os.getenv('WORKER_PROCESSES', cpu_count() - 1))
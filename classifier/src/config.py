import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'file-uploads')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'file-classifier')
    
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB = os.getenv('MONGODB_DB', 'fileupload')
    
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', '../upload/uploads') 
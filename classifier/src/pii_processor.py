from presidio_analyzer import AnalyzerEngine
from minio import Minio
from .config import Config

class Processor:
    def __init__(self):
        self.analyzer = AnalyzerEngine()

        # Initialize MinIO client - these should come from config
        self.minio_client = Minio(
            endpoint=Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=Config.MINIO_SECURE
        )

        self.bucket_name = Config.MINIO_BUCKET_NAME
    
    def process_file(self, file_path: str) -> dict:
        try:
            # Extract just the filename from the path
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path
            
            print(f"Fetching object from MinIO - bucket: {self.bucket_name}, file: {file_name}")
            
            # Ensure both parameters are strings
            bucket_name = str(self.bucket_name)
            file_name = str(file_name)
            
            # Get object data from MinIO using just the filename
            data = self.minio_client.get_object(bucket_name, file_name)
            
            # Read into memory and decode
            text = data.read().decode('utf-8')
            
            # Use Presidio for analysis
            analyzer_results = self.analyzer.analyze(
                text=text,
                language='en'
            )
            
            return [
                {
                    "entity_type": finding.entity_type,
                    "start": finding.start,
                    "end": finding.end,
                    "score": finding.score
                }
                for finding in analyzer_results
            ]
        except Exception as e:
            print(f"Error processing file in MinIO: {str(e)}")
            print(f"Bucket: {self.bucket_name}, File path: {file_path}")
            raise 
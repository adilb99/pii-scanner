from presidio_analyzer import AnalyzerEngine
from minio import Minio

class Processor:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        # Initialize MinIO client - these should come from config
        self.minio_client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False  # Set to True in production
        )
        
        self.bucket_name = 'uploads'
    
    def process_file(self, file_path: str) -> dict:
        try:
            file_name = file_path.split('/')[-1]
            # Get object data from MinIO
            data = self.minio_client.get_object(self.bucket_name, file_name)
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
            print(f"Error processing file: {str(e)}")
            raise 
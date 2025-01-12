from .kafka_consumer import KafkaClient
from .mongodb_client import MongoDBClient
from .pii_processor import Processor
import os

def main():
    kafka_client = KafkaClient()
    mongodb_client = MongoDBClient()
    pii_processor = Processor()
    
    print("Starting PII classifier worker...")
    
    for message in kafka_client.consume_messages():
        try:
            file_id = message.get('fileId')
            file_path = message.get('fileLocation')
            library = message.get('library')
            
            if not file_id or not file_path:
                continue
                
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            absolute_file_path = os.path.join(project_root, 'upload', file_path)
            
            # Process the file
            processed = pii_processor.process_file(absolute_file_path)
            
            results = []
            if library == 'pii-extract':
                results = processed['pii_extract_findings']
            else:
                results = processed['presidio_findings']
            
            # Update status to completed with results
            mongodb_client.update_file_status(
                file_id,
                "DONE"
            )
            
            mongodb_client.create_classification_results(file_id, results)
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            if file_id:
                mongodb_client.update_file_status(
                    file_id,
                    "ERROR",
                    {"error": str(e)}
                )

if __name__ == "__main__":
    main() 
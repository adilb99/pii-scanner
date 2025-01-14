from .constants import FileStatus
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
            
            if not file_id or not file_path:
                print("file id or path not provided, skipping...")
                continue
                
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            absolute_file_path = os.path.join(project_root, 'upload', file_path)
            
            # Process the file
            results = pii_processor.process_file(absolute_file_path)
            
            # Update status to completed with results
            mongodb_client.update_file_status(
                file_id,
                FileStatus.DONE.value
            )
            
            mongodb_client.create_classification_results(file_id, results)
            
            print(f'Successfully proccesed file with id=${file_id} ...')
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            if file_id:
                mongodb_client.update_file_status(
                    file_id,
                    FileStatus.ERROR.value,
                    str(e),
                )

if __name__ == "__main__":
    main() 
from .constants import FileStatus
from .kafka_consumer import KafkaClient
from .mongodb_client import MongoDBClient
from .pii_processor import Processor
from multiprocessing import Pool, cpu_count
from .config import Config

def process_message(message):
    """Worker function to process individual messages"""
    mongodb_client = None
    try:
        mongodb_client = MongoDBClient()
        pii_processor = Processor()

        file_id = message.get('fileId')
        file_path = message.get('fileLocation')
        
        if not file_id or not file_path:
            print("file id or path not provided, skipping...")
            return False  # Explicitly return False for invalid messages
        
        # Process the file
        results = pii_processor.process_file(file_path)
        
        # Update status to completed with results
        mongodb_client.update_file_status(
            file_id,
            FileStatus.DONE.value
        )
        
        mongodb_client.create_classification_results(file_id, results)
        
        print(f"Successfully processed file with id={file_id}")
        return True  # Explicitly return True for success
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        if mongodb_client and file_id:
            try:
                mongodb_client.update_file_status(
                    file_id,
                    FileStatus.ERROR.value,
                    str(e),
                )
            except Exception as mongo_error:
                print(f"Failed to update error status in MongoDB: {str(mongo_error)}")
        return False  # Explicitly return False for errors

def main():
    kafka_client = KafkaClient()
    num_workers = Config.WORKER_PROCESSES or max(1, cpu_count() - 1)
    
    print(f"Starting PII classifier worker with {num_workers} workers...")
    
    # Create a process pool
    with Pool(processes=num_workers) as pool:
        try:
            # Get messages from Kafka
            consumer = kafka_client.consume_messages()
            
            # Process messages and handle results
            for message in consumer:
                result = pool.apply_async(process_message, (message,))
                success = result.get()  # Wait for the result
                
                # Send success/failure back to kafka consumer
                consumer.send(success)
                
        except KeyboardInterrupt:
            print("Shutting down workers...")
            pool.terminate()
        finally:
            pool.close()
            pool.join()

if __name__ == "__main__":
    main() 
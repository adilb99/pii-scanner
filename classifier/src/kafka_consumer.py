from kafka import KafkaConsumer, TopicPartition, KafkaProducer, OffsetAndMetadata
from kafka.errors import KafkaError
import json
from .config import Config
import time
import traceback

class KafkaClient:
    def __init__(self):
        try:
            self.consumer = KafkaConsumer(
                Config.KAFKA_TOPIC,
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                group_id=Config.KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                max_poll_interval_ms=300000,
            )
            
            # Initialize the producer for DLQ
            self.producer = KafkaProducer(
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            self.dlq_topic = f"{Config.KAFKA_TOPIC}.dlq"
            self.max_retries = Config.KAFKA_MAX_RETRIES
            self.retry_interval = Config.KAFKA_RETRY_INTERVAL
            
        except Exception as e:
            print(f"Error initializing Kafka client: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
        
    def _send_to_dlq(self, message, error):
        """Send failed message to Dead Letter Queue"""
        try:
            dlq_message = {
                'original_message': message.value,
                'error': str(error),
                'topic': message.topic,
                'partition': message.partition,
                'offset': message.offset,
                'timestamp': message.timestamp,
            }
            
            self.producer.send(self.dlq_topic, value=dlq_message)
            print(f"Message sent to DLQ: {dlq_message}")
            
        except Exception as e:
            print(f"Error sending to DLQ: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
        
    def consume_messages(self):
        retry_count = {}
        
        try:
            while True:
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    continue
                
                for tp, messages in message_batch.items():
                    for message in messages:
                        message_key = f"{message.topic}-{message.partition}-{message.offset}"
                        current_retries = retry_count.get(message_key, 0)
                        
                        try:
                            print(f"Processing message: {message.value}")
                            success = yield message.value
                            
                            # Only commit if processing was successful
                            if success:
                                self.consumer.commit({
                                    TopicPartition(message.topic, message.partition): 
                                        OffsetAndMetadata(message.offset + 1, None)
                                })
                                
                                if message_key in retry_count:
                                    del retry_count[message_key]
                            else:
                                raise Exception("Processing returned False")
                            
                        except Exception as e:
                            print(f"Error processing message {message_key}: {str(e)}")
                            print(f"Traceback: {traceback.format_exc()}")
                            
                            if current_retries < self.max_retries:
                                print(f"Retrying message {message_key}. Attempt {current_retries + 1} of {self.max_retries}")
                                retry_count[message_key] = current_retries + 1
                                time.sleep(self.retry_interval * (current_retries + 1))  # Exponential backoff
                                self.consumer.seek(TopicPartition(message.topic, message.partition), message.offset)
                            else:
                                print(f"Max retries reached for message {message_key}, sending to DLQ")
                                self._send_to_dlq(message, e)
                                # Only commit after sending to DLQ
                                self.consumer.commit({
                                    TopicPartition(message.topic, message.partition): 
                                        OffsetAndMetadata(message.offset + 1, None)
                                })
                                del retry_count[message_key]
                                
        except KafkaError as e:
            print(f"Kafka error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
        except Exception as e:
            print(f"Unexpected error in consume_messages: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise 
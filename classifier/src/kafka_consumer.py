from kafka import KafkaConsumer
import json
from .config import Config

class KafkaClient:
    def __init__(self):
        self.consumer = KafkaConsumer(
            Config.KAFKA_TOPIC,
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
            group_id=Config.KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )
    
    def consume_messages(self):
        try:
            for message in self.consumer:
                yield message.value
        except Exception as e:
            print(f"Error consuming Kafka messages: {str(e)}")
            raise 
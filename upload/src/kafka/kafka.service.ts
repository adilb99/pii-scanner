// src/kafka/kafka.service.ts

import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { Kafka, Producer } from 'kafkajs';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class KafkaService implements OnModuleInit, OnModuleDestroy {
  private kafka: Kafka;
  private producer: Producer;

  async onModuleInit() {
    this.kafka = new Kafka({
      brokers: [process.env.KAFKA_BROKER || 'localhost:9092'],
      clientId: 'upload' + uuidv4(),
    });
    this.producer = this.kafka.producer();
    await this.producer.connect();
  }

  async produce(topic: string, data: any) {
    await this.producer.send({
      topic,
      messages: [{ value: JSON.stringify(data) }],
    });
  }

  async onModuleDestroy() {
    await this.producer.disconnect();
  }
}

import { Module } from '@nestjs/common';
import { MulterModule } from '@nestjs/platform-express';
import { MongooseModule } from '@nestjs/mongoose';
import { FileController } from './file.controller';
import { FileService } from './file.service';
import {
  FileInventory,
  FileInventorySchema,
} from './schemas/file-inventory.schema';
import { KafkaModule } from 'src/kafka/kafka.module';
import {
  DataScanResult,
  DataScanResultSchema,
} from './schemas/data-scan-result.schema';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    MulterModule.register({
      dest: './uploads', // Directory to store files
    }),
    MongooseModule.forFeature([
      { name: FileInventory.name, schema: FileInventorySchema },
      { name: DataScanResult.name, schema: DataScanResultSchema },
    ]),
    KafkaModule,
    ConfigModule,
  ],
  controllers: [FileController],
  providers: [FileService],
})
export class FileModule {}

// src/file/file.service.ts

import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import {
  FileInventory,
  FileInventoryDocument,
} from './schemas/file-inventory.schema';
import { UploadFileDto } from './dto/upload-file.dto';
import { KafkaService } from '../kafka/kafka.service';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';
import { DataScanResultDocument } from './schemas/data-scan-result.schema';
import { DataScanResult } from './schemas/data-scan-result.schema';

@Injectable()
export class FileService {
  constructor(
    @InjectModel(FileInventory.name)
    private fileInventoryModel: Model<FileInventoryDocument>,
    @InjectModel(DataScanResult.name)
    private dataScanResultModel: Model<DataScanResultDocument>,
    private readonly kafkaService: KafkaService,
  ) {}

  /**
   * Save or update file metadata in fileInventory.
   */
  async registerFile(
    file: Express.Multer.File,
    dto: UploadFileDto,
  ): Promise<FileInventory> {
    // Generate or use existing fileId (DTO can override)
    const fileId = dto.fileId || uuidv4();

    const fileDoc = {
      fileId,
      fileName: file.originalname,
      fileType: path.extname(file.originalname).replace('.', ''), // "csv", "txt", etc.
      fileLocation: './uploads/' + file.filename,
      library: dto.library || 'presidio',
      status: 'UPLOADED',
    };

    // Upsert in MongoDB using fileId as the unique identifier
    const result = await this.fileInventoryModel.findOneAndUpdate(
      { fileId },
      { $set: fileDoc },
      { upsert: true, new: true },
    );

    return result;
  }

  /**
   * Send a Kafka message for the classifier to process.
   */
  async notifyClassifier(fileDoc: FileInventory) {
    await this.kafkaService.produce('data_classification', {
      fileId: fileDoc.fileId,
      fileName: fileDoc.fileName,
      fileLocation: fileDoc.fileLocation,
      library: fileDoc.library,
      fileType: fileDoc.fileType,
    });
  }

  /**
   * Retrieves file status from the fileInventory collection.
   */
  async getFileStatus(fileId: string) {
    const doc = await this.fileInventoryModel.findOne({ fileId }).exec();
    if (!doc) {
      return null;
    }
    return {
      fileId: doc.fileId,
      fileName: doc.fileName,
      status: doc.status,
      errorReason: doc.errorReason,
    };
  }

  /**
   * Retrieves classification results from dataScanResult collection.
   */
  async getFileResults(fileId: string) {
    const file = await this.dataScanResultModel.findOne({ fileId }).exec();
    if (!file) {
      return null;
    }
    return {
      fileId: file.fileId,
      results: file.results,
    };
  }
}

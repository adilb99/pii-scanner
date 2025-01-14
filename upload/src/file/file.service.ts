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
import { Client } from 'minio';

@Injectable()
export class FileService {
  private minioClient: Client;
  private readonly bucketName = 'uploads';

  constructor(
    @InjectModel(FileInventory.name)
    private fileInventoryModel: Model<FileInventoryDocument>,
    @InjectModel(DataScanResult.name)
    private dataScanResultModel: Model<DataScanResultDocument>,
    private readonly kafkaService: KafkaService,
  ) {
    // Initialize MinIO client
    this.minioClient = new Client({
      endPoint: 'localhost', // or from config
      port: 9000, // or from config
      useSSL: false, // true for production
      accessKey: 'minioadmin', // from config
      secretKey: 'minioadmin', // from config
    });

    // Ensure bucket exists
    this.initBucket();
  }

  private async initBucket() {
    const bucketExists = await this.minioClient.bucketExists(this.bucketName);
    if (!bucketExists) {
      await this.minioClient.makeBucket(this.bucketName);
    }
  }

  /**
   * Save or update file metadata in fileInventory.
   */
  async registerFile(
    file: Express.Multer.File,
    dto: UploadFileDto,
  ): Promise<FileInventory> {
    const fileExtName = path.extname(file.originalname);
    const nameWithoutExt = file.originalname.replace(fileExtName, '');
    const randomSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    const finalName = `${nameWithoutExt}-${randomSuffix}${fileExtName}`;

    // Generate or use existing fileId (DTO can override)
    const fileId = dto.fileId || uuidv4();

    const fileMeta = {
      fileId,
      fileName: file.originalname,
      fileType: path.extname(file.originalname).replace('.', ''),
      fileLocation: finalName,
      status: 'REQ',
    };

    // Create initial document in MongoDB
    const result = await this.fileInventoryModel.findOneAndUpdate(
      { fileId },
      { $set: fileMeta },
      { upsert: true, new: true },
    );

    // Start upload in background in case file is large and takes time
    this.uploadFileToMinio(fileId, finalName, file).catch(async (error) => {
      // Update DB with error status if upload fails
      await this.fileInventoryModel.findOneAndUpdate(
        { fileId },
        {
          $set: {
            status: 'ERROR',
            errorReason: error.message,
          },
        },
      );
    });

    return result;
  }

  private async uploadFileToMinio(
    fileId: string,
    finalName: string,
    file: Express.Multer.File,
  ): Promise<void> {
    try {
      await this.minioClient.putObject(
        this.bucketName,
        finalName,
        file.buffer,
        file.size,
        {
          'Content-Type': file.mimetype,
        },
      );

      // Update status to UPLOADED once complete
      await this.fileInventoryModel.findOneAndUpdate(
        { fileId },
        {
          $set: {
            status: 'UPLOADED',
            uploadedAt: new Date(),
          },
        },
      );

      // Only notify classifier after successful upload
      await this.notifyClassifier({
        fileId,
        fileName: file.filename,
        fileLocation: finalName,
      });
    } catch (error) {
      throw error; // This will be caught by the error handler in registerFile
    }
  }

  /**
   * Send a Kafka message for the classifier to process.
   */
  async notifyClassifier(fileDoc: Partial<FileInventory>) {
    await this.kafkaService.produce('data_classification', {
      fileId: fileDoc.fileId,
      fileName: fileDoc.fileName,
      fileLocation: fileDoc.fileLocation,
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

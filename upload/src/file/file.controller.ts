// src/file/file.controller.ts

import {
  Controller,
  Post,
  Get,
  Param,
  Body,
  UseInterceptors,
  UploadedFile,
  NotFoundException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { FileService } from './file.service';
import { UploadFileDto } from './dto/upload-file.dto';
import { memoryStorage } from 'multer';

@Controller('file')
export class FileController {
  constructor(private readonly fileService: FileService) {}

  /**
   * POST /file/upload
   * - Accepts multipart/form-data (the `file` field)
   * - Saves file under ./uploads (or /tmp if desired)
   * - Updates fileInventory (status="UPLOADED")
   * - Sends Kafka message
   */
  @Post('upload')
  @UseInterceptors(
    FileInterceptor('file', {
      storage: memoryStorage(),
    }),
  )
  async uploadFile(
    @UploadedFile() file: Express.Multer.File,
    @Body() uploadDto: UploadFileDto,
  ) {
    if (!file) {
      throw new NotFoundException('No file uploaded');
    }

    const fileDoc = await this.fileService.registerFile(file, uploadDto);

    return {
      message: 'File upload request created successfully.',
      fileId: fileDoc.fileId,
      status: fileDoc.status,
    };
  }

  /**
   * GET /file/status/:fileId
   * - Returns the file's status from fileInventory
   */
  @Get('status/:fileId')
  async getStatus(@Param('fileId') fileId: string) {
    const status = await this.fileService.getFileStatus(fileId);
    if (!status) {
      throw new NotFoundException('File not found');
    }
    return status;
  }

  /**
   * GET /file/results/:fileId
   * - Returns classification results from dataScanResult
   */
  @Get('results/:fileId')
  async getResults(@Param('fileId') fileId: string) {
    const results = await this.fileService.getFileResults(fileId);
    if (!results) {
      throw new NotFoundException('No classification results for this file');
    }
    return results;
  }
}

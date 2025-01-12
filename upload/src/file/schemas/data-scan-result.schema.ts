// src/file/schemas/data-scan-result.schema.ts

import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

@Schema({ collection: 'dataScanResult' })
export class DataScanResult {
  // Ties to the file's ID from fileInventory
  @Prop({ required: true, unique: true })
  fileId: string;

  // The classifier’s or scanning results (could be any structure you need)
  @Prop()
  results: Record<string, any>[];

  @Prop({ default: Date.now })
  createdAt: Date;

  @Prop({ default: Date.now })
  updatedAt: Date;
}

export type DataScanResultDocument = DataScanResult & Document;
export const DataScanResultSchema =
  SchemaFactory.createForClass(DataScanResult);

// src/file/schemas/file-inventory.schema.ts

import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

/**
 * fileInventory document example:
 * {
 *   fileId: "64b1f7eabcd1234567890",
 *   fileName: "employees.csv",
 *   fileType: "csv",
 *   fileLocation: "/tmp/employees.csv",
 *   library: "pii-extract",
 *   status: "REQ"
 * }
 *
 * Possible status values: "REQ", "UPLOADED", "DONE", "ERROR"
 */
@Schema({ collection: 'fileInventory' })
export class FileInventory {
  // In Mongo, _id is used by default; you can store fileId as a separate field or alias.
  @Prop({ required: true, unique: true })
  fileId: string;

  @Prop()
  fileName: string;

  @Prop()
  fileType: string;

  @Prop()
  fileLocation: string;

  @Prop()
  library: string;

  @Prop({ default: 'REQ' })
  status: string;

  @Prop({ default: null })
  errorReason: string;
}

export type FileInventoryDocument = FileInventory & Document;
export const FileInventorySchema = SchemaFactory.createForClass(FileInventory);

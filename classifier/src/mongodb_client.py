import datetime
from pymongo import MongoClient
from .config import Config
from datetime import datetime, timezone

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.MONGODB_DB]
        self.fileInventory = self.db['fileInventory']
        self.dataScanResult = self.db['dataScanResult']

    def create_classification_results(self, file_id: str, classification_results: list = None):
        try:
            now = datetime.now(timezone.utc)   
            if classification_results is not None:
                self.dataScanResult.update_one(
                    {"fileId": file_id},
                    {
                        "$set": {
                            "fileId": file_id,
                            "results": classification_results,  # array of objects
                            "updatedAt": now
                        },
                        "$setOnInsert": {"createdAt": now}
                    },
                    upsert=True
                )
        except Exception as e:
            print(f"Error creating results in MongoDB: {str(e)}")
            raise
            
            

    def update_file_status(self, file_id: str, status: str):
        """
        Updates the file status in `fileInventory` and, if classification results
        are provided, writes them to `dataScanResult`.

        :param file_id: The fileId (unique identifier in NestJS).
        :param status: New status, e.g. "REQ", "UPLOADED", "DONE", "ERROR".
        :param classification_results: A list of dicts, each containing:
               {
                 "piiType": "Email",
                 "piiValue": "john.doe@xyz.com",
                 "location": "row: 3, column: Email"
               }
        """
        try:
            
            
            # 2) Update file status in fileInventory
            self.fileInventory.update_one(
                {"fileId": file_id},  # matches the NestJS schema
                {
                    "$set": {
                        "status": status
                    }
                }
            )
        except Exception as e:
            print(f"Error updating MongoDB: {str(e)}")
            raise

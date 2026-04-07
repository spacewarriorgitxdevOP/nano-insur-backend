"""
P1 - MongoDB Atlas Connection
Single collection, no TTL as specified.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None
    claims_collection = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB Atlas"""
        try:
            cls.client = AsyncIOMotorClient(
                MONGO_URI,
                server_api=ServerApi('1'),
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000
            )
            # Verify connection
            await cls.client.admin.command('ping')
            cls.db = cls.client[DB_NAME]
            cls.claims_collection = cls.db[COLLECTION_NAME]
            
            # Create indexes for fast queries
            await cls.claims_collection.create_index("claim_id", unique=True)
            await cls.claims_collection.create_index("status")
            await cls.claims_collection.create_index("created_at")
            
            logger.info(f"✅ Connected to MongoDB Atlas - DB: {DB_NAME}")
            print(f"✅ Connected to MongoDB Atlas - DB: {DB_NAME}")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            print(f"❌ MongoDB connection failed: {e}")
            raise

    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB Atlas"""
        if cls.client:
            cls.client.close()
            logger.info("🔌 MongoDB disconnected")

    @classmethod
    def get_collection(cls):
        """Get the claims collection"""
        if cls.claims_collection is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls.claims_collection
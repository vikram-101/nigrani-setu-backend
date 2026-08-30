from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongo_uri)
db = client[settings.db_name]

# Collections — one per entity in the system
users_collection = db["users"]
institutes_collection = db["institutes"]
inspectors_collection = db["inspectors"]
assignments_collection = db["assignments"]
reports_collection = db["reports"]
alerts_collection = db["alerts"]


async def ping_database():
    """Called on startup to confirm the Atlas/local connection actually works."""
    await client.admin.command("ping")

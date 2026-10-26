"""Retryable deletion of optional enrollment photos after profile deactivation."""
import asyncio
import logging
from datetime import datetime, timezone
from core.database import get_database
from core.azure_face import _cfg

logger = logging.getLogger(__name__)


async def process_pending_deletions():
    db = get_database()
    async for job in db.biometric_cleanup.find({"status": "pending"}).limit(50):
        pid = job["_id"]
        try:
            config = _cfg()
            if config["blob_conn_str"]:
                from azure.storage.blob import BlobServiceClient
                def remove():
                    with BlobServiceClient.from_connection_string(config["blob_conn_str"]) as service:
                        container = service.get_container_client(config["blob_container"])
                        for blob in container.list_blobs(name_starts_with=f"persons/{pid}/"):
                            container.delete_blob(blob.name, delete_snapshots="include")
                await asyncio.to_thread(remove)
            elif job.get("has_photo"):
                raise RuntimeError("Blob storage configuration is required to delete existing photos")
            await db.biometric_cleanup.update_one({"_id": pid}, {"$set": {"status": "complete", "completed_at": datetime.now(timezone.utc)}})
        except Exception:
            logger.exception("Enrollment photo deletion pending for profile %s", pid)
            await db.biometric_cleanup.update_one({"_id": pid}, {"$inc": {"attempts": 1}, "$set": {"last_attempt_at": datetime.now(timezone.utc)}})


async def cleanup_loop():
    while True:
        try:
            await process_pending_deletions()
        except Exception:
            logger.exception("Biometric cleanup worker failed; it will retry")
        await asyncio.sleep(60)

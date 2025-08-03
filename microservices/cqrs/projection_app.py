# CQRS Projection Service - Background Event Processor

import asyncio
import logging
import sys
import os

# Add shared events to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from read_store import CQRSReadStore
from projectors import CQRSProjectionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main projection service"""
    logger.info("Starting CQRS Projection Service...")
    
    try:
        # Create read store
        read_store = CQRSReadStore()
        
        # Create projection service
        projection_service = CQRSProjectionService(read_store)
        
        # Start the service
        await projection_service.start()
        
        logger.info("CQRS Projection Service is running. Press Ctrl+C to stop.")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
    except Exception as e:
        logger.error(f"Error in projection service: {e}")
        raise
    finally:
        # Cleanup
        if 'projection_service' in locals():
            await projection_service.stop()
        
        logger.info("CQRS Projection Service stopped")

if __name__ == "__main__":
    asyncio.run(main())

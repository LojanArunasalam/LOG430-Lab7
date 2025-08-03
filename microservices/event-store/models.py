# Event Store Models for MongoDB

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import logging

logger = logging.getLogger(__name__)

class MongoEventStore:
    """MongoDB Event Store for storing and querying events"""
    
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            connection_string = os.getenv(
                "MONGODB_URL", 
                "mongodb://admin:admin@mongodb_event_store:27017/event_store?authSource=admin"
            )
        
        self.client = MongoClient(connection_string)
        self.db = self.client.event_store
        self.events_collection = self.db.stored_events
        self.snapshots_collection = self.db.event_snapshots
        
        # Create indexes for better performance
        self._create_indexes()
        
    def _create_indexes(self):
        """Create MongoDB indexes for efficient querying"""
        try:
            # Events collection indexes
            self.events_collection.create_index("event_id", unique=True)
            self.events_collection.create_index("event_type")
            self.events_collection.create_index("aggregate_type")
            self.events_collection.create_index("aggregate_id")
            self.events_collection.create_index("correlation_id")
            self.events_collection.create_index("timestamp")
            self.events_collection.create_index([
                ("aggregate_type", ASCENDING),
                ("aggregate_id", ASCENDING),
                ("version", ASCENDING)
            ])
            
            # Snapshots collection indexes
            self.snapshots_collection.create_index([
                ("aggregate_type", ASCENDING),
                ("aggregate_id", ASCENDING)
            ], unique=True)
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def store_event(self, event_data: Dict[str, Any]) -> bool:
        """Store an event in MongoDB"""
        try:
            # Ensure timestamp is a datetime object
            if 'timestamp' in event_data and isinstance(event_data['timestamp'], str):
                event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            elif 'timestamp' not in event_data:
                event_data['timestamp'] = datetime.utcnow()
            
            # Add version if not present
            if 'version' not in event_data:
                event_data['version'] = 1
            
            result = self.events_collection.insert_one(event_data)
            logger.info(f"Event stored with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return False

    def get_events(self, 
                   event_type: Optional[str] = None,
                   aggregate_type: Optional[str] = None,
                   aggregate_id: Optional[str] = None,
                   correlation_id: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Query events with optional filters"""
        
        query = {}
        if event_type:
            query['event_type'] = event_type
        if aggregate_type:
            query['aggregate_type'] = aggregate_type
        if aggregate_id:
            query['aggregate_id'] = aggregate_id
        if correlation_id:
            query['correlation_id'] = correlation_id
        
        cursor = self.events_collection.find(query).sort("timestamp", ASCENDING).limit(limit)
        events = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            
        return events

    def get_aggregate_events(self, aggregate_type: str, aggregate_id: str) -> List[Dict[str, Any]]:
        """Get all events for a specific aggregate ordered by version"""
        
        query = {
            'aggregate_type': aggregate_type,
            'aggregate_id': aggregate_id
        }
        
        cursor = self.events_collection.find(query).sort("version", ASCENDING)
        events = list(cursor)
        
        # Convert ObjectId to string
        for event in events:
            event['_id'] = str(event['_id'])
            
        return events

    def store_snapshot(self, 
                      aggregate_type: str, 
                      aggregate_id: str, 
                      snapshot_data: Dict[str, Any], 
                      version: int) -> bool:
        """Store an aggregate snapshot"""
        try:
            snapshot = {
                'aggregate_type': aggregate_type,
                'aggregate_id': aggregate_id,
                'snapshot_data': snapshot_data,
                'version': version,
                'timestamp': datetime.utcnow()
            }
            
            # Use upsert to replace existing snapshot
            result = self.snapshots_collection.replace_one(
                {'aggregate_type': aggregate_type, 'aggregate_id': aggregate_id},
                snapshot,
                upsert=True
            )
            
            logger.info(f"Snapshot stored for {aggregate_type}:{aggregate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing snapshot: {e}")
            return False

    def get_snapshot(self, aggregate_type: str, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest snapshot for an aggregate"""
        
        snapshot = self.snapshots_collection.find_one({
            'aggregate_type': aggregate_type,
            'aggregate_id': aggregate_id
        })
        
        if snapshot:
            snapshot['_id'] = str(snapshot['_id'])
            
        return snapshot

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored events"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$event_type',
                        'count': {'$sum': 1},
                        'latest': {'$max': '$timestamp'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            stats = list(self.events_collection.aggregate(pipeline))
            
            total_events = self.events_collection.count_documents({})
            
            return {
                'total_events': total_events,
                'by_type': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'total_events': 0, 'by_type': []}

    def close(self):
        """Close MongoDB connection"""
        self.client.close()

# Global event store instance
event_store = MongoEventStore()

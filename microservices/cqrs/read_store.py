# CQRS Read Store - MongoDB Implementation for Optimized Queries

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
import logging
from typing import List, Optional, Dict, Any
from models import OrderReadModel, InventoryReadModel, UserOrderSummaryReadModel

logger = logging.getLogger(__name__)

class CQRSReadStore:
    """MongoDB-based read store optimized for queries"""
    
    def __init__(self, mongodb_url: str = "mongodb://mongodb:27017", database_name: str = "cqrs_read_db"):
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # Create indexes for optimized queries
            await self._create_indexes()
            
            logger.info(f"Connected to CQRS Read Store: {self.database_name}")
            
        except Exception as e:
            logger.error(f"Error connecting to CQRS Read Store: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from CQRS Read Store")
    
    async def _create_indexes(self):
        """Create indexes for optimized queries"""
        try:
            # Order indexes
            await self.db.orders.create_index([("order_id", ASCENDING)], unique=True)
            await self.db.orders.create_index([("user_id", ASCENDING)])
            await self.db.orders.create_index([("status", ASCENDING)])
            await self.db.orders.create_index([("created_at", DESCENDING)])
            await self.db.orders.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
            
            # Inventory indexes
            await self.db.inventory.create_index([("product_id", ASCENDING)], unique=True)
            await self.db.inventory.create_index([("available_quantity", ASCENDING)])
            await self.db.inventory.create_index([("reorder_level", ASCENDING)])
            
            # User order summary indexes
            await self.db.user_summaries.create_index([("user_id", ASCENDING)], unique=True)
            await self.db.user_summaries.create_index([("total_orders", DESCENDING)])
            await self.db.user_summaries.create_index([("total_spent", DESCENDING)])
            
            logger.info("CQRS Read Store indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # ========================================================================
    # ORDER READ OPERATIONS
    # ========================================================================
    
    async def get_order(self, order_id: str) -> Optional[OrderReadModel]:
        """Get order by ID"""
        try:
            doc = await self.db.orders.find_one({"order_id": order_id})
            if doc:
                return self._doc_to_order_model(doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            raise
    
    async def get_user_orders(self, user_id: int, status: str = None) -> List[OrderReadModel]:
        """Get orders for a user, optionally filtered by status"""
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            
            cursor = self.db.orders.find(query).sort("created_at", DESCENDING)
            orders = []
            
            async for doc in cursor:
                orders.append(self._doc_to_order_model(doc))
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting user orders for user {user_id}: {e}")
            raise
    
    async def get_orders_by_status(self, status: str) -> List[OrderReadModel]:
        """Get all orders with specific status"""
        try:
            cursor = self.db.orders.find({"status": status}).sort("created_at", DESCENDING)
            orders = []
            
            async for doc in cursor:
                orders.append(self._doc_to_order_model(doc))
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting orders by status {status}: {e}")
            raise
    
    async def get_recent_orders(self, limit: int = 50) -> List[OrderReadModel]:
        """Get recent orders"""
        try:
            cursor = self.db.orders.find().sort("created_at", DESCENDING).limit(limit)
            orders = []
            
            async for doc in cursor:
                orders.append(self._doc_to_order_model(doc))
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting recent orders: {e}")
            raise
    
    # ========================================================================
    # INVENTORY READ OPERATIONS
    # ========================================================================
    
    async def get_product_inventory(self, product_id: int) -> Optional[InventoryReadModel]:
        """Get inventory for a specific product"""
        try:
            doc = await self.db.inventory.find_one({"product_id": product_id})
            if doc:
                return self._doc_to_inventory_model(doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting inventory for product {product_id}: {e}")
            raise
    
    async def get_all_inventory(self) -> List[InventoryReadModel]:
        """Get all inventory items"""
        try:
            cursor = self.db.inventory.find().sort("product_id", ASCENDING)
            inventories = []
            
            async for doc in cursor:
                inventories.append(self._doc_to_inventory_model(doc))
            
            return inventories
            
        except Exception as e:
            logger.error(f"Error getting all inventory: {e}")
            raise
    
    async def get_low_stock_items(self) -> List[InventoryReadModel]:
        """Get items with low stock (available <= reorder_level)"""
        try:
            # MongoDB aggregation to find low stock items
            pipeline = [
                {
                    "$match": {
                        "$expr": {
                            "$lte": ["$available_quantity", "$reorder_level"]
                        }
                    }
                },
                {
                    "$sort": {"available_quantity": ASCENDING}
                }
            ]
            
            cursor = self.db.inventory.aggregate(pipeline)
            inventories = []
            
            async for doc in cursor:
                inventories.append(self._doc_to_inventory_model(doc))
            
            return inventories
            
        except Exception as e:
            logger.error(f"Error getting low stock items: {e}")
            raise
    
    # ========================================================================
    # USER SUMMARY READ OPERATIONS
    # ========================================================================
    
    async def get_user_summary(self, user_id: int) -> Optional[UserOrderSummaryReadModel]:
        """Get user order summary"""
        try:
            doc = await self.db.user_summaries.find_one({"user_id": user_id})
            if doc:
                return self._doc_to_user_summary_model(doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user summary for user {user_id}: {e}")
            raise
    
    async def get_top_customers(self, limit: int = 10) -> List[UserOrderSummaryReadModel]:
        """Get top customers by total spent"""
        try:
            cursor = self.db.user_summaries.find().sort("total_spent", DESCENDING).limit(limit)
            summaries = []
            
            async for doc in cursor:
                summaries.append(self._doc_to_user_summary_model(doc))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting top customers: {e}")
            raise
    
    # ========================================================================
    # ANALYTICS QUERIES
    # ========================================================================
    
    async def get_order_statistics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get order statistics for a date range"""
        try:
            match_stage = {}
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                match_stage["created_at"] = date_filter
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"},
                        "avg_order_value": {"$avg": "$total_amount"},
                        "orders_by_status": {
                            "$push": {
                                "status": "$status",
                                "amount": "$total_amount"
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_orders": 1,
                        "total_revenue": 1,
                        "avg_order_value": 1,
                        "orders_by_status": 1
                    }
                }
            ]
            
            result = await self.db.orders.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                
                # Process status counts
                status_counts = {}
                for order in stats.get("orders_by_status", []):
                    status = order["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                stats["status_counts"] = status_counts
                return stats
            else:
                return {
                    "total_orders": 0,
                    "total_revenue": 0.0,
                    "avg_order_value": 0.0,
                    "status_counts": {}
                }
            
        except Exception as e:
            logger.error(f"Error getting order statistics: {e}")
            raise
    
    # ========================================================================
    # WRITE OPERATIONS (for event projections)
    # ========================================================================
    
    async def upsert_order(self, order_model: OrderReadModel):
        """Upsert order read model"""
        try:
            doc = self._order_model_to_doc(order_model)
            await self.db.orders.replace_one(
                {"order_id": order_model.order_id},
                doc,
                upsert=True
            )
            logger.debug(f"Upserted order: {order_model.order_id}")
            
        except Exception as e:
            logger.error(f"Error upserting order {order_model.order_id}: {e}")
            raise
    
    async def upsert_inventory(self, inventory_model: InventoryReadModel):
        """Upsert inventory read model"""
        try:
            doc = self._inventory_model_to_doc(inventory_model)
            await self.db.inventory.replace_one(
                {"product_id": inventory_model.product_id},
                doc,
                upsert=True
            )
            logger.debug(f"Upserted inventory: {inventory_model.product_id}")
            
        except Exception as e:
            logger.error(f"Error upserting inventory {inventory_model.product_id}: {e}")
            raise
    
    async def upsert_user_summary(self, summary_model: UserOrderSummaryReadModel):
        """Upsert user summary read model"""
        try:
            doc = self._user_summary_model_to_doc(summary_model)
            await self.db.user_summaries.replace_one(
                {"user_id": summary_model.user_id},
                doc,
                upsert=True
            )
            logger.debug(f"Upserted user summary: {summary_model.user_id}")
            
        except Exception as e:
            logger.error(f"Error upserting user summary {summary_model.user_id}: {e}")
            raise
    
    # ========================================================================
    # CONVERSION HELPERS
    # ========================================================================
    
    def _doc_to_order_model(self, doc: Dict) -> OrderReadModel:
        """Convert MongoDB document to OrderReadModel"""
        model = OrderReadModel()
        model.order_id = doc.get("order_id", "")
        model.user_id = doc.get("user_id", 0)
        model.user_email = doc.get("user_email", "")
        model.user_name = doc.get("user_name", "")
        model.total_amount = doc.get("total_amount", 0.0)
        model.status = doc.get("status", "")
        model.created_at = doc.get("created_at")
        model.updated_at = doc.get("updated_at")
        model.items = doc.get("items", [])
        model.payment_info = doc.get("payment_info", {})
        model.shipping_info = doc.get("shipping_info", {})
        model.timeline = doc.get("timeline", [])
        return model
    
    def _order_model_to_doc(self, model: OrderReadModel) -> Dict:
        """Convert OrderReadModel to MongoDB document"""
        return {
            "order_id": model.order_id,
            "user_id": model.user_id,
            "user_email": model.user_email,
            "user_name": model.user_name,
            "total_amount": model.total_amount,
            "status": model.status,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "items": model.items,
            "payment_info": model.payment_info,
            "shipping_info": model.shipping_info,
            "timeline": model.timeline
        }
    
    def _doc_to_inventory_model(self, doc: Dict) -> InventoryReadModel:
        """Convert MongoDB document to InventoryReadModel"""
        model = InventoryReadModel()
        model.product_id = doc.get("product_id", 0)
        model.product_name = doc.get("product_name", "")
        model.available_quantity = doc.get("available_quantity", 0)
        model.reserved_quantity = doc.get("reserved_quantity", 0)
        model.total_quantity = doc.get("total_quantity", 0)
        model.reorder_level = doc.get("reorder_level", 0)
        model.last_restocked = doc.get("last_restocked")
        model.pending_orders = doc.get("pending_orders", [])
        return model
    
    def _inventory_model_to_doc(self, model: InventoryReadModel) -> Dict:
        """Convert InventoryReadModel to MongoDB document"""
        return {
            "product_id": model.product_id,
            "product_name": model.product_name,
            "available_quantity": model.available_quantity,
            "reserved_quantity": model.reserved_quantity,
            "total_quantity": model.total_quantity,
            "reorder_level": model.reorder_level,
            "last_restocked": model.last_restocked,
            "pending_orders": model.pending_orders
        }
    
    def _doc_to_user_summary_model(self, doc: Dict) -> UserOrderSummaryReadModel:
        """Convert MongoDB document to UserOrderSummaryReadModel"""
        model = UserOrderSummaryReadModel()
        model.user_id = doc.get("user_id", 0)
        model.user_email = doc.get("user_email", "")
        model.total_orders = doc.get("total_orders", 0)
        model.total_spent = doc.get("total_spent", 0.0)
        model.avg_order_value = doc.get("avg_order_value", 0.0)
        model.last_order_date = doc.get("last_order_date")
        model.favorite_products = doc.get("favorite_products", [])
        model.order_statuses = doc.get("order_statuses", {})
        return model
    
    def _user_summary_model_to_doc(self, model: UserOrderSummaryReadModel) -> Dict:
        """Convert UserOrderSummaryReadModel to MongoDB document"""
        return {
            "user_id": model.user_id,
            "user_email": model.user_email,
            "total_orders": model.total_orders,
            "total_spent": model.total_spent,
            "avg_order_value": model.avg_order_value,
            "last_order_date": model.last_order_date,
            "favorite_products": model.favorite_products,
            "order_statuses": model.order_statuses
        }

# CQRS Package Init

from .models import (
    # Commands
    Command, CreateOrderCommand, ProcessPaymentCommand, UpdateInventoryCommand,
    # Queries  
    Query, GetOrderQuery, GetUserOrdersQuery, GetInventoryQuery, GetOrderStatisticsQuery,
    # Read Models
    OrderReadModel, InventoryReadModel, UserOrderSummaryReadModel,
    # Handlers
    CommandHandler, QueryHandler,
    CreateOrderCommandHandler, ProcessPaymentCommandHandler,
    GetOrderQueryHandler, GetUserOrdersQueryHandler, GetInventoryQueryHandler
)

from .read_store import CQRSReadStore
from .projectors import (
    EventProjector, OrderProjector, InventoryProjector, 
    UserSummaryProjector, CQRSProjectionService
)

__all__ = [
    # Commands
    "Command", "CreateOrderCommand", "ProcessPaymentCommand", "UpdateInventoryCommand",
    # Queries
    "Query", "GetOrderQuery", "GetUserOrdersQuery", "GetInventoryQuery", "GetOrderStatisticsQuery", 
    # Read Models
    "OrderReadModel", "InventoryReadModel", "UserOrderSummaryReadModel",
    # Handlers
    "CommandHandler", "QueryHandler",
    "CreateOrderCommandHandler", "ProcessPaymentCommandHandler",
    "GetOrderQueryHandler", "GetUserOrdersQueryHandler", "GetInventoryQueryHandler",
    # Infrastructure
    "CQRSReadStore",
    "EventProjector", "OrderProjector", "InventoryProjector", 
    "UserSummaryProjector", "CQRSProjectionService"
]

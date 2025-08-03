# CQRS Demo Script - Test the CQRS Implementation

import asyncio
import aiohttp
import json
from datetime import datetime
import time

# API Base URLs (through Kong Gateway)
KONG_BASE = "http://localhost:8000"
COMMAND_API = f"{KONG_BASE}/cqrs/commands"
QUERY_API = f"{KONG_BASE}/cqrs/queries"

async def demo_cqrs_workflow():
    """Demonstrate CQRS workflow with commands and queries"""
    
    print("🚀 CQRS Event Broker Demo - Lab 7")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. CREATE ORDER COMMAND
        print("\n📝 1. Creating Order (COMMAND)")
        order_data = {
            "user_id": 123,
            "product_id": 456,
            "quantity": 2
        }
        
        async with session.post(f"{COMMAND_API}/orders", json=order_data) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                order_id = result["data"]["order_id"]
                print(f"   ✅ Order Created: {order_id}")
            else:
                print(f"   ❌ Failed to create order: {result.get('error')}")
                return
        
        # 2. WAIT FOR PROJECTION
        print("\n⏳ 2. Waiting for event projection...")
        await asyncio.sleep(3)  # Give time for events to be projected
        
        # 3. QUERY ORDER (READ)
        print(f"\n📖 3. Querying Order {order_id} (QUERY)")
        async with session.get(f"{QUERY_API}/orders/{order_id}") as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            
            if result.get("success"):
                order = result["data"]
                print(f"   ✅ Order Found:")
                print(f"      ID: {order['order_id']}")
                print(f"      User: {order['user_id']}")
                print(f"      Status: {order['status']}")
                print(f"      Created: {order['created_at']}")
                print(f"      Timeline: {len(order['timeline'])} events")
            else:
                print(f"   ❌ Order not found: {result.get('error')}")
        
        # 4. PROCESS PAYMENT COMMAND
        print(f"\n💳 4. Processing Payment for Order {order_id} (COMMAND)")
        payment_data = {
            "order_id": order_id,
            "amount": 99.99,
            "payment_method": "credit_card"
        }
        
        async with session.post(f"{COMMAND_API}/payments", json=payment_data) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                payment_id = result["data"]["payment_id"]
                print(f"   ✅ Payment Initiated: {payment_id}")
        
        # 5. WAIT FOR PAYMENT PROJECTION
        print("\n⏳ 5. Waiting for payment event projection...")
        await asyncio.sleep(3)
        
        # 6. QUERY UPDATED ORDER
        print(f"\n📖 6. Querying Updated Order {order_id} (QUERY)")
        async with session.get(f"{QUERY_API}/orders/{order_id}") as resp:
            result = await resp.json()
            
            if result.get("success"):
                order = result["data"]
                print(f"   ✅ Updated Order:")
                print(f"      Status: {order['status']}")
                print(f"      Payment Info: {order.get('payment_info', 'None')}")
                print(f"      Timeline: {len(order['timeline'])} events")
                
                for i, event in enumerate(order['timeline']):
                    print(f"        {i+1}. {event['event']} at {event['timestamp']}")
        
        # 7. INVENTORY COMMANDS
        print(f"\n📦 7. Inventory Operations (COMMANDS)")
        
        # Reserve inventory
        inventory_data = {
            "product_id": 456,
            "quantity_change": 2,
            "operation": "reserve"
        }
        
        async with session.post(f"{COMMAND_API}/inventory", json=inventory_data) as resp:
            result = await resp.json()
            print(f"   Reserve Inventory - Status: {resp.status}")
            print(f"   Response: {json.dumps(result, indent=2)}")
        
        # 8. WAIT FOR INVENTORY PROJECTION
        print("\n⏳ 8. Waiting for inventory event projection...")
        await asyncio.sleep(3)
        
        # 9. QUERY INVENTORY
        print(f"\n📦 9. Querying Product Inventory (QUERY)")
        async with session.get(f"{QUERY_API}/inventory/456") as resp:
            result = await resp.json()
            
            if result.get("success"):
                inventory = result["data"]
                if inventory:
                    print(f"   ✅ Inventory Found:")
                    print(f"      Product: {inventory['product_id']}")
                    print(f"      Available: {inventory['available_quantity']}")
                    print(f"      Reserved: {inventory['reserved_quantity']}")
                    print(f"      Total: {inventory['total_quantity']}")
                    print(f"      Low Stock Alert: {inventory['low_stock_alert']}")
                else:
                    print("   ℹ️ No inventory data yet (still processing)")
        
        # 10. QUERY USER ORDERS
        print(f"\n👤 10. Querying User Orders (QUERY)")
        async with session.get(f"{QUERY_API}/users/123/orders") as resp:
            result = await resp.json()
            
            if result.get("success"):
                orders = result["data"]
                print(f"   ✅ Found {result.get('count', 0)} orders for user 123:")
                for order in orders[:3]:  # Show first 3
                    print(f"      - {order['order_id']}: {order['status']} (${order['total_amount']})")
        
        # 11. QUERY RECENT ORDERS
        print(f"\n🕒 11. Querying Recent Orders (QUERY)")
        async with session.get(f"{QUERY_API}/orders/recent?limit=5") as resp:
            result = await resp.json()
            
            if result.get("success"):
                orders = result["data"]
                print(f"   ✅ Found {result.get('count', 0)} recent orders:")
                for order in orders:
                    print(f"      - {order['order_id']}: {order['status']} by user {order['user_id']}")
        
        # 12. QUERY ORDER STATISTICS
        print(f"\n📊 12. Querying Order Statistics (QUERY)")
        async with session.get(f"{QUERY_API}/statistics/orders") as resp:
            result = await resp.json()
            
            if result.get("success"):
                stats = result["data"]
                print(f"   ✅ Order Statistics:")
                print(f"      Total Orders: {stats.get('total_orders', 0)}")
                print(f"      Total Revenue: ${stats.get('total_revenue', 0):.2f}")
                print(f"      Average Order Value: ${stats.get('avg_order_value', 0):.2f}")
                print(f"      Status Counts: {stats.get('status_counts', {})}")

async def test_command_query_separation():
    """Test that commands and queries are properly separated"""
    
    print("\n🔍 Testing Command-Query Separation")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        
        # Test that query service can't accept commands
        print("\n❌ Testing Query Service Rejects Commands")
        try:
            async with session.post(f"{QUERY_API}/orders", json={"test": "data"}) as resp:
                print(f"   Status: {resp.status} (should be 404 or 405)")
        except Exception as e:
            print(f"   Expected error: {e}")
        
        # Test that command service can't handle queries directly
        print("\n❌ Testing Command Service Focuses on Commands")
        async with session.get(f"{COMMAND_API}/health") as resp:
            result = await resp.json()
            print(f"   Command Service Health: {result.get('status')}")
            print(f"   Available Handlers: {result.get('handlers', [])}")

async def main():
    """Main demo function"""
    try:
        await demo_cqrs_workflow()
        await test_command_query_separation()
        
        print("\n🎉 CQRS Demo Completed!")
        print("\nKey CQRS Benefits Demonstrated:")
        print("✅ Command-Query Separation: Different services for write/read")
        print("✅ Optimized Read Models: Fast queries with denormalized data")  
        print("✅ Event-Driven Updates: Real-time projection of events")
        print("✅ Scalability: Independent scaling of command/query sides")
        print("✅ Analytics: Rich aggregated data for business insights")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure all CQRS services are running:")
        print("- docker-compose up cqrs_command cqrs_query cqrs_projector")

if __name__ == "__main__":
    asyncio.run(main())

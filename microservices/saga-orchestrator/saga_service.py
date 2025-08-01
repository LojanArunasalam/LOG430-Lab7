import requests
import logging
import time
import datetime
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from state_machine import OrderStateMachine, OrderState
from models import SagaInstance, SagaStatus
from prometheus_client import Counter, Histogram, Gauge
from py_api_saga.py_api_saga import SagaAssembler

# Configure logging
logger = logging.getLogger(__name__)
# Prometheus metrics
saga_counter = Counter('saga_total', 'Total number of sagas', ['status'])
saga_duration = Histogram('saga_duration_seconds', 'Saga execution duration')
saga_step_duration = Histogram('saga_step_duration_seconds', 'Individual step duration', ['step'])
active_sagas = Gauge('active_sagas_total', 'Number of currently active sagas')

saga_state_counter = Counter('saga_states_total', 'Total number of state transitions', ['state'])
saga_current_states = Gauge('saga_current_states', 'Current number of sagas in each state', ['state'])

class SagaService:
    
    def __init__(self, db: Session):
        self.db = db
        self.state_machine = OrderStateMachine(db)
        self.timeout = 30  # seconds
        
        self.services = {
            'warehouse': 'http://microservices_warehouse-1:8002',
            'ecommerce': 'http://microservices_ecommerce:8004'
        }

        self._initialize_state_metrics()

    def _initialize_state_metrics(self):
        """Initialize current state metrics on startup"""
        try:
            # Import here to avoid circular imports
            from sqlalchemy import func
            
            # Get current state counts
            state_counts = self.db.query(
                SagaInstance.current_state,
                func.count(SagaInstance.id).label('count')
            ).filter(
                SagaInstance.saga_status.in_([
                    SagaStatus.STARTED.value,
                    SagaStatus.IN_PROGRESS.value,
                    SagaStatus.COMPENSATING.value
                ])
            ).group_by(SagaInstance.current_state).all()
            
            # Initialize all state gauges
            for state in OrderState:
                saga_current_states.labels(state=state.value).set(0)
            
            # Set current counts
            for state, count in state_counts:
                saga_current_states.labels(state=state).set(count)
                
            logger.info("State metrics initialized")
        except Exception as e:
            logger.error(f"Error initializing state metrics: {e}")
    
    def start_order_saga(self, customer_id: int, product_id: int, store_id: int, 
                        cart_id: int, quantity: int) -> Dict[str, Any]:
        """Start a new order saga"""
        saga_start_time = time.time()
        
        try:
            # Generate unique order ID
            order_id = int(time.time() * 1000) % 1000000
            
            # Create saga instance
            saga = self.state_machine.create_saga(
                order_id=order_id,
                customer_id=customer_id,
                product_id=product_id,
                store_id=store_id,
                cart_id=cart_id,
                quantity=quantity,
            )
            
            active_sagas.inc()
            logger.info(f"Starting saga {saga.id} for order {order_id}")
            
            # Prepare order data
            order_data = {
                'saga_id': saga.id,
                'order_id': order_id,
                'customer_id': customer_id,
                'product_id': product_id,
                'store_id': store_id,
                'cart_id': cart_id,
                'quantity': quantity,
            }
            
            # Execute saga steps
            success = self._execute_saga_steps(saga.id, order_data)
            
            # Record metrics
            saga_duration.observe(time.time() - saga_start_time)
            
            if success:
                saga_counter.labels(status='completed').inc()
                active_sagas.dec()
                return {
                    'saga_id': saga.id,
                    'order_id': order_id,
                    'status': 'completed',
                    'current_state': OrderState.ORDER_CONFIRMED.value,
                    'message': 'Order processed successfully',
                    'created_at': datetime.datetime.now().isoformat()
                }
            else:
                saga_counter.labels(status='failed').inc()
                active_sagas.dec()
                saga = self.state_machine.get_saga(saga.id)
                return {
                    'saga_id': saga.id,
                    'order_id': order_id,
                    'status': 'failed',
                    'current_state': saga.current_state,
                    'message': saga.error_message or 'Order processing failed',
                    'created_at': datetime.datetime.now().isoformat()

                }
                
        except Exception as e:
            saga_counter.labels(status='error').inc()
            active_sagas.dec()
            logger.error(f"Error starting saga: {str(e)}")
            return {
                'saga_id': None,
                'order_id': None,
                'status': 'error',
                'current_state': 'error',
                'message': f'Failed to start saga: {str(e)}',
                'created_at': datetime.datetime.now().isoformat()
            }
    
    def _execute_saga_steps(self, saga_id: int, order_data: Dict[str, Any]) -> bool:
        """Execute all saga steps in sequence"""

        try:    
            # Step 1: Verify stock availability
            if not self._verify_stock(saga_id, order_data):
                return False
            
            # Step 2: Reserve stock
            if not self._reserve_stock(saga_id, order_data):
                return False
            
            # Step 3: Process payment
            if not self._initiate_checkout(saga_id, order_data):
                return False
            
            # Step 4: Confirm order
            if not self._confirm_order(saga_id, order_data):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing saga steps: {str(e)}")
            self._start_compensation(saga_id, str(e))
            return False
    
    def _verify_stock(self, saga_id: int, order_data: Dict[str, Any]) -> bool:
        """Step 1: Verify stock availability"""
        step_start = time.time()
        
        try:
            self.state_machine.log_step_started(saga_id, "verify_stock", order_data)
            
            response = requests.get(
                f"{self.services['warehouse']}/api/v1/stocks/product/{order_data['product_id']}/store/{order_data['store_id']}",
                timeout=self.timeout
            )
            
            saga_step_duration.labels(step='verify_stock').observe(time.time() - step_start)
            
            if response.status_code == 200:
                result = response.json()
                available_quantity = result.get('quantite', 0)
                
                if available_quantity >= order_data['quantity']:
                    self.state_machine.log_step_completed(saga_id, "verify_stock", result)
                    self.state_machine.transition_to(saga_id, OrderState.STOCK_VERIFIED)
                    return True
                else:
                    error_msg = f"Insufficient stock: available={available_quantity}, required={order_data['quantity']}"
                    self.state_machine.log_step_failed(saga_id, "verify_stock", error_msg, result)
                    self.state_machine.transition_to(saga_id, OrderState.CANCELLED, error_msg)
                    return False
            else:
                error_msg = f"Stock check failed: {response.status_code}"
                self.state_machine.log_step_failed(saga_id, "verify_stock", error_msg)
                self.state_machine.transition_to(saga_id, OrderState.CANCELLED, error_msg)
                return False
                
        except requests.RequestException as e:
            error_msg = f"Error calling warehouse service: {str(e)}"
            self.state_machine.log_step_failed(saga_id, "verify_stock", error_msg)
            self.state_machine.transition_to(saga_id, OrderState.CANCELLED, error_msg)
            return False
    
    def _reserve_stock(self, saga_id: int, order_data: Dict[str, Any]) -> bool:
        """Step 2: Add item to cart (reserve stock)"""
        step_start = time.time()
        
        try:
            self.state_machine.log_step_started(saga_id, "reserve_stock", order_data)
            
            # Call ecommerce service to add item to cart
            response = requests.post(
                f"{self.services['ecommerce']}/api/v1/cart/add-item",
                json={
                    'cart': order_data['cart_id'],
                    'product': order_data['product_id'],
                    'quantite': order_data['quantity'],
                    'store_id': order_data['store_id']
                },
                timeout=self.timeout
            )
            
            saga_step_duration.labels(step='reserve_stock').observe(time.time() - step_start)
            
            if response.status_code == 200:
                result = response.json()
                self.state_machine.log_step_completed(saga_id, "reserve_stock", result)
                self.state_machine.transition_to(saga_id, OrderState.STOCK_RESERVED)
                
                # Add compensation action for removing item from cart
                self.state_machine.add_compensation_action(
                    saga_id, 
                    f"remove_item_from_cart:{order_data['cart_id']}:{order_data['product_id']}"
                )
                return True
            else:
                error_msg = f"Adding item to cart failed: {response.status_code} - {response.text}"
                self.state_machine.log_step_failed(saga_id, "reserve_stock", error_msg)
                self._start_compensation(saga_id, error_msg)
                return False
        except requests.RequestException as e:
            error_msg = f"Error calling ecommerce service: {str(e)}"
            self.state_machine.log_step_failed(saga_id, "reserve_stock", error_msg)
            self._start_compensation(saga_id, error_msg)
            return False
    
    def _initiate_checkout(self, saga_id: int, order_data: Dict[str, Any]) -> bool:
        """Step 3: Process payment"""
        step_start = time.time()
        
        try:
            self.state_machine.log_step_started(saga_id, "process_payment", order_data)
            
            # First initiate checkout
            checkout_response = requests.post(
                f"{self.services['ecommerce']}/api/v1/checkout/initiate",
                json={
                    'cart_id': order_data['cart_id']
                },
                timeout=self.timeout
            )
            
            if checkout_response.status_code == 200:
                checkout_result = checkout_response.json()
                checkout_id = checkout_result.get('id')
                
                # Update saga with checkout_id
                saga = self.state_machine.get_saga(saga_id)
                saga.checkout_id = checkout_id
                self.db.commit()
                
                # Then complete checkout (process payment)
                complete_response = requests.post(
                    f"{self.services['ecommerce']}/api/v1/checkout/{checkout_id}/complete",
                    timeout=self.timeout
                )
                
                saga_step_duration.labels(step='process_payment').observe(time.time() - step_start)
                
                if complete_response.status_code == 200:
                    result = complete_response.json()
                    self.state_machine.log_step_completed(saga_id, "process_payment", result)
                    self.state_machine.transition_to(saga_id, OrderState.PAYMENT_PROCESSED)
                    
                    # Add compensation action for payment cancellation
                    self.state_machine.add_compensation_action(saga_id, f"cancel_checkout:{checkout_id}")
                    return True
                else:
                    error_msg = f"Payment processing failed: {complete_response.status_code} - {complete_response.text}"
                    self.state_machine.log_step_failed(saga_id, "process_payment", error_msg)
                    self._start_compensation(saga_id, error_msg)
                    return False
            else:
                error_msg = f"Checkout initiation failed: {checkout_response.status_code} - {checkout_response.text}"
                self.state_machine.log_step_failed(saga_id, "process_payment", error_msg)
                self._start_compensation(saga_id, error_msg)
                return False
                
        except requests.RequestException as e:
            error_msg = f"Error calling ecommerce service: {str(e)}"
            self.state_machine.log_step_failed(saga_id, "process_payment", error_msg)
            self._start_compensation(saga_id, error_msg)
            return False
    
    def _confirm_order(self, saga_id: int, order_data: Dict[str, Any]) -> bool:
        """Step 4: Confirm order (finalize the saga)"""
        step_start = time.time()
        
        try:
            self.state_machine.log_step_started(saga_id, "confirm_order", order_data)
            
            # Order confirmation is implicit when payment is processed
            # This step is mainly for logging and final state transition
            result = {
                'order_confirmed': True, 
                'saga_id': saga_id,
                'order_id': order_data['order_id']
            }
            
            self.state_machine.log_step_completed(saga_id, "confirm_order", result)
            self.state_machine.transition_to(saga_id, OrderState.ORDER_CONFIRMED)
            
            saga_step_duration.labels(step='confirm_order').observe(time.time() - step_start)
            
            logger.info(f"Order {order_data['order_id']} confirmed successfully via saga {saga_id}")
            return True
            
        except Exception as e:
            error_msg = f"Error confirming order: {str(e)}"
            self.state_machine.log_step_failed(saga_id, "confirm_order", error_msg)
            self._start_compensation(saga_id, error_msg)
            return False
    
    def _start_compensation(self, saga_id: int, error_message: str):
        """Start compensation process to undo completed steps"""
        logger.info(f"Starting compensation for saga {saga_id}: {error_message}")
        
        try:
            self.state_machine.transition_to(saga_id, OrderState.COMPENSATION_STARTED, error_message)
            
            # Get compensation actions
            actions = self.state_machine.get_compensation_actions(saga_id)
            
            # Execute compensation actions in reverse order
            for action in reversed(actions):
                try:
                    self._execute_compensation_action(saga_id, action)
                except Exception as e:
                    logger.error(f"Compensation action failed for saga {saga_id}: {str(e)}")
            
            # Mark saga as cancelled
            self.state_machine.transition_to(saga_id, OrderState.CANCELLED)
            
        except Exception as e:
            logger.error(f"Error during compensation for saga {saga_id}: {str(e)}")
    
    def _execute_compensation_action(self, saga_id: int, action: str):
        """Execute a specific compensation action"""
        logger.info(f"Executing compensation action '{action}' for saga {saga_id}")
        
        try:
            if action.startswith("remove_item_from_cart:"):
            # Parse: remove_item_from_cart:cart_id:product_id
                parts = action.split(":")
                if len(parts) == 3:
                    cart_id, product_id = parts[1], parts[2]
                    
                    # Call ecommerce service to clear items from cart
                    response = requests.delete(
                        f"{self.services['ecommerce']}/api/v1/cart/{cart_id}/clear",
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Successfully cleared items in cart {cart_id}")
                    else:
                        logger.error(f"Failed to clear cart {cart_id}: {response.status_code}")
            elif action.startswith("restore_stock:"):
                # Parse: restore_stock:product_id:store_id:quantity
                parts = action.split(":")
                if len(parts) == 4:
                    product_id, store_id, quantity = parts[1], parts[2], parts[3]
                    
                    # Note: You would need to implement a restore stock endpoint
                    # For now, we'll log it as we don't have this endpoint yet
                    logger.info(f"Would restore stock: product={product_id}, store={store_id}, quantity={quantity}")
                    
            elif action.startswith("cancel_checkout:"):
                # Parse: cancel_checkout:checkout_id
                checkout_id = action.split(":")[1]
                
                response = requests.put(
                    f"{self.services['ecommerce']}/api/v1/checkout/{checkout_id}/cancel",
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully cancelled checkout {checkout_id}")
                else:
                    logger.error(f"Failed to cancel checkout {checkout_id}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error executing compensation action '{action}': {str(e)}")
    
    def get_saga_status(self, saga_id: int) -> Optional[Dict[str, Any]]:
        """Get current status of a saga"""
        return self.state_machine.get_saga_summary(saga_id)
    
    def get_saga_by_order_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get saga status by order ID"""
        saga = self.state_machine.get_saga_by_order_id(order_id)
        if saga:
            return self.state_machine.get_saga_summary(saga.id)
        return None
    
    def list_active_sagas(self) -> list:
        """Get list of all active (non-completed) sagas"""
        active_sagas = self.db.query(SagaInstance).filter(
            SagaInstance.saga_status.in_([
                SagaStatus.STARTED.value,
                SagaStatus.IN_PROGRESS.value,
                SagaStatus.COMPENSATING.value
            ])
        ).all()
        
        return [self.state_machine.get_saga_summary(saga.id) for saga in active_sagas]
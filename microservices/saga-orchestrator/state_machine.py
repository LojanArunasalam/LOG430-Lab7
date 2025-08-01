from sqlalchemy.orm import Session
from models import SagaInstance, SagaStep, OrderState, SagaStatus
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    OrderState.CREATED: [OrderState.STOCK_VERIFIED, OrderState.CANCELLED],
    OrderState.STOCK_VERIFIED: [OrderState.STOCK_RESERVED, OrderState.CANCELLED],
    OrderState.STOCK_RESERVED: [OrderState.PAYMENT_PROCESSED, OrderState.COMPENSATION_STARTED],
    OrderState.PAYMENT_PROCESSED: [OrderState.ORDER_CONFIRMED, OrderState.COMPENSATION_STARTED],
    OrderState.ORDER_CONFIRMED: [],  # Final state
    OrderState.COMPENSATION_STARTED: [OrderState.CANCELLED],
    OrderState.CANCELLED: []  # Final state
}

saga_state_counter = None
saga_current_states = None


def initialize_metrics():
    """Initialize metrics - call this from saga_service.py"""
    global saga_state_counter, saga_current_states
    from saga_service import saga_state_counter as state_counter
    from saga_service import saga_current_states as current_states
    saga_state_counter = state_counter
    saga_current_states = current_states

class OrderStateMachine:
    """Manages state transitions for order sagas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.VALID_TRANSITIONS = VALID_TRANSITIONS
        if saga_state_counter is None:
            initialize_metrics()
    
    def create_saga(self, order_id: int, customer_id: int, product_id: int, 
                   store_id: int, cart_id: int, quantity: int, amount: float = None) -> SagaInstance:
        """Create a new saga instance"""
        saga = SagaInstance(
            order_id=order_id,
            customer_id=customer_id,
            product_id=product_id,
            store_id=store_id,
            cart_id=cart_id,
            quantity=quantity,
            amount=amount,
            current_state=OrderState.CREATED.value,
            saga_status=SagaStatus.STARTED.value
        )
        
        self.db.add(saga)
        self.db.commit()
        self.db.refresh(saga)
        
        logger.info(f"Created saga {saga.id} for order {order_id}")
        return saga
    
    def get_saga(self, saga_id: int) -> Optional[SagaInstance]:
        """Get saga instance by ID"""
        return self.db.query(SagaInstance).filter(SagaInstance.id == saga_id).first()
    
    def get_saga_by_order_id(self, order_id: int) -> Optional[SagaInstance]:
        """Get saga instance by order ID"""
        return self.db.query(SagaInstance).filter(SagaInstance.order_id == order_id).first()
    
    def transition_to(self, saga_id: int, new_state: OrderState, error_message: str = None) -> bool:
        """Transition saga to a new state"""
        saga = self.get_saga(saga_id)
        if not saga:
            logger.error(f"Saga {saga_id} not found")
            return False
        
        current_state = OrderState(saga.current_state)
        
        # Check if transition is valid
        if new_state not in self.VALID_TRANSITIONS[current_state]:
            logger.error(f"Invalid transition from {current_state.value} to {new_state.value} for saga {saga_id}")
            return False
        
        # Update state
        old_state = saga.current_state
        saga.current_state = new_state.value
        saga.updated_at = datetime.utcnow()
        
        if error_message:
            saga.error_message = error_message
        
        # Update saga status based on state
        if new_state == OrderState.ORDER_CONFIRMED:
            saga.saga_status = SagaStatus.COMPLETED.value
        elif new_state == OrderState.CANCELLED:
            saga.saga_status = SagaStatus.FAILED.value
        elif new_state == OrderState.COMPENSATION_STARTED:
            saga.saga_status = SagaStatus.COMPENSATING.value
        else:
            saga.saga_status = SagaStatus.IN_PROGRESS.value
        
        self.db.commit()

        # UPDATE METRICS HERE
        if saga_state_counter:
            saga_state_counter.labels(state=new_state.value).inc()
        
        if saga_current_states:
            self._update_current_state_metrics()
        
        logger.info(f"Saga {saga_id} transitioned from {old_state} to {new_state.value}")
        return True

    def _update_current_state_metrics(self):
        """Update the current state gauge metrics"""
        try:
            # Query current state counts for active sagas
            state_counts = self.db.query(
                SagaInstance.current_state,
                count(SagaInstance.id).label('count')
            ).filter(
                SagaInstance.saga_status.in_([
                    SagaStatus.STARTED.value,
                    SagaStatus.IN_PROGRESS.value,
                    SagaStatus.COMPENSATING.value
                ])
            ).group_by(SagaInstance.current_state).all()
            
            # Reset all gauges to 0
            for state in OrderState:
                if saga_current_states:
                    saga_current_states.labels(state=state.value).set(0)
            
            # Set current counts
            for state, count in state_counts:
                if saga_current_states:
                    saga_current_states.labels(state=state).set(count)
                    
        except Exception as e:
            logger.error(f"Error updating state metrics: {e}")
    
    def log_step_started(self, saga_id: int, step_name: str, request_data: Dict[str, Any]):
        """Log that a saga step has started"""
        step = SagaStep(
            saga_id=saga_id,
            step_name=step_name,
            step_status="started",
            request_data=json.dumps(request_data) if request_data else None
        )
        
        self.db.add(step)
        self.db.commit()
        
        logger.info(f"Started step '{step_name}' for saga {saga_id}")
        return step
    
    def log_step_completed(self, saga_id: int, step_name: str, response_data: Dict[str, Any] = None):
        """Log that a saga step has completed successfully"""
        step = self.db.query(SagaStep).filter(
            SagaStep.saga_id == saga_id,
            SagaStep.step_name == step_name,
            SagaStep.step_status == "started"
        ).first()
        
        if step:
            step.step_status = "completed"
            step.completed_at = datetime.utcnow()
            step.response_data = json.dumps(response_data) if response_data else None
            self.db.commit()
            
            logger.info(f"Completed step '{step_name}' for saga {saga_id}")
        else:
            logger.warning(f"Step '{step_name}' not found for saga {saga_id}")
    
    def log_step_failed(self, saga_id: int, step_name: str, error_message: str, response_data: Dict[str, Any] = None):
        """Log that a saga step has failed"""
        step = self.db.query(SagaStep).filter(
            SagaStep.saga_id == saga_id,
            SagaStep.step_name == step_name,
            SagaStep.step_status == "started"
        ).first()
        
        if step:
            step.step_status = "failed"
            step.completed_at = datetime.utcnow()
            step.error_message = error_message
            step.response_data = json.dumps(response_data) if response_data else None
            self.db.commit()
            
            logger.error(f"Failed step '{step_name}' for saga {saga_id}: {error_message}")
        else:
            logger.warning(f"Step '{step_name}' not found for saga {saga_id}")
    
    def add_compensation_action(self, saga_id: int, action: str):
        """Add a compensation action to be executed if saga fails"""
        saga = self.get_saga(saga_id)
        if not saga:
            return
        
        current_actions = []
        if saga.compensation_actions:
            try:
                current_actions = json.loads(saga.compensation_actions)
            except json.JSONDecodeError:
                current_actions = []
        
        current_actions.append(action)
        saga.compensation_actions = json.dumps(current_actions)
        self.db.commit()
        
        logger.info(f"Added compensation action '{action}' to saga {saga_id}")
    
    def get_compensation_actions(self, saga_id: int) -> List[str]:
        """Get list of compensation actions for a saga"""
        saga = self.get_saga(saga_id)
        if not saga or not saga.compensation_actions:
            return []
        
        try:
            return json.loads(saga.compensation_actions)
        except json.JSONDecodeError:
            logger.error(f"Invalid compensation actions JSON for saga {saga_id}")
            return []
    
    def is_valid_transition(self, current_state: OrderState, new_state: OrderState) -> bool:
        """Check if a state transition is valid"""
        return new_state in self.VALID_TRANSITIONS.get(current_state, [])
    
    def get_possible_transitions(self, saga_id: int) -> List[OrderState]:
        """Get list of possible next states for a saga"""
        saga = self.get_saga(saga_id)
        if not saga:
            return []
        
        current_state = OrderState(saga.current_state)
        return self.VALID_TRANSITIONS.get(current_state, [])
    
    def get_saga_steps(self, saga_id: int) -> List[SagaStep]:
        """Get all steps for a saga"""
        return self.db.query(SagaStep).filter(SagaStep.saga_id == saga_id).order_by(SagaStep.started_at).all()
    
    def is_saga_complete(self, saga_id: int) -> bool:
        """Check if saga has reached a final state"""
        saga = self.get_saga(saga_id)
        if not saga:
            return False
        
        current_state = OrderState(saga.current_state)
        return current_state in [OrderState.ORDER_CONFIRMED, OrderState.CANCELLED]
    
    def get_saga_summary(self, saga_id: int) -> Dict[str, Any]:
        """Get a summary of the saga state and steps"""
        saga = self.get_saga(saga_id)
        if not saga:
            return {}
        
        steps = self.get_saga_steps(saga_id)
        
        return {
            "saga_id": saga.id,
            "order_id": saga.order_id,
            "current_state": saga.current_state,
            "saga_status": saga.saga_status,
            "created_at": saga.created_at.isoformat() if saga.created_at else None,
            "updated_at": saga.updated_at.isoformat() if saga.updated_at else None,
            "error_message": saga.error_message,
            "steps_count": len(steps),
            "completed_steps": len([s for s in steps if s.step_status == "completed"]),
            "failed_steps": len([s for s in steps if s.step_status == "failed"]),
            "is_complete": self.is_saga_complete(saga_id)
        }
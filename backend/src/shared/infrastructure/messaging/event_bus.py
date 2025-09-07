"""
Event bus for inter-context communication.
"""
import asyncio
import logging
from typing import Dict, List, Callable, Any
from abc import ABC, abstractmethod

from src.shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event."""
        pass


class EventBus:
    """Event bus for domain events."""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middleware: List[Callable] = []
        self._logger = logger
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        self._logger.info(f"Subscribed handler {handler.__class__.__name__} to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                self._logger.info(f"Unsubscribed handler {handler.__class__.__name__} from {event_type}")
            except ValueError:
                self._logger.warning(f"Handler {handler.__class__.__name__} not found for {event_type}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the event bus."""
        self._middleware.append(middleware)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        event_type = type(event).__name__
        
        self._logger.info(f"Publishing event: {event_type}")
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                await middleware(event)
            except Exception as e:
                self._logger.error(f"Middleware error for {event_type}: {e}")
        
        # Get handlers for this event type
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            self._logger.warning(f"No handlers found for event type: {event_type}")
            return
        
        # Execute handlers asynchronously
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._execute_handler(handler, event))
            tasks.append(task)
        
        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_handler(self, handler: EventHandler, event: DomainEvent) -> None:
        """Execute a single event handler."""
        try:
            await handler.handle(event)
            self._logger.debug(f"Handler {handler.__class__.__name__} executed successfully for {type(event).__name__}")
        except Exception as e:
            self._logger.error(f"Handler {handler.__class__.__name__} failed for {type(event).__name__}: {e}")
    
    def get_subscribers(self, event_type: str) -> List[EventHandler]:
        """Get all subscribers for an event type."""
        return self._handlers.get(event_type, []).copy()
    
    def get_all_event_types(self) -> List[str]:
        """Get all registered event types."""
        return list(self._handlers.keys())
    
    def clear_subscribers(self, event_type: str) -> None:
        """Clear all subscribers for an event type."""
        if event_type in self._handlers:
            del self._handlers[event_type]
            self._logger.info(f"Cleared all subscribers for {event_type}")
    
    def clear_all_subscribers(self) -> None:
        """Clear all subscribers."""
        self._handlers.clear()
        self._logger.info("Cleared all subscribers")


class EventMiddleware:
    """Base class for event middleware."""
    
    async def __call__(self, event: DomainEvent) -> None:
        """Execute middleware logic."""
        pass


class LoggingMiddleware(EventMiddleware):
    """Middleware for logging events."""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def __call__(self, event: DomainEvent) -> None:
        """Log event details."""
        self.logger.info(f"Event {type(event).__name__} occurred at {event.occurred_at}")
        self.logger.debug(f"Event data: {event.to_dict()}")


class MetricsMiddleware(EventMiddleware):
    """Middleware for collecting event metrics."""
    
    def __init__(self):
        self.event_counts: Dict[str, int] = {}
        self.handler_execution_times: Dict[str, List[float]] = {}
    
    async def __call__(self, event: DomainEvent) -> None:
        """Collect metrics for the event."""
        event_type = type(event).__name__
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
    
    def get_event_counts(self) -> Dict[str, int]:
        """Get event counts."""
        return self.event_counts.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            'total_events': sum(self.event_counts.values()),
            'event_types': len(self.event_counts),
            'event_counts': self.event_counts
        }


class EventStore:
    """Simple event store for persistence."""
    
    def __init__(self):
        self._events: List[DomainEvent] = []
        self._logger = logging.getLogger(__name__)
    
    async def store(self, event: DomainEvent) -> None:
        """Store an event."""
        self._events.append(event)
        self._logger.debug(f"Stored event: {type(event).__name__}")
    
    async def get_events_by_type(self, event_type: str) -> List[DomainEvent]:
        """Get events by type."""
        return [event for event in self._events if type(event).__name__ == event_type]
    
    async def get_events_by_conversation(self, conversation_id: str) -> List[DomainEvent]:
        """Get events by conversation ID."""
        return [
            event for event in self._events
            if hasattr(event, 'conversation_id') and event.conversation_id == conversation_id
        ]
    
    async def get_all_events(self) -> List[DomainEvent]:
        """Get all events."""
        return self._events.copy()
    
    async def clear_events(self) -> None:
        """Clear all events."""
        self._events.clear()
        self._logger.info("Cleared all events")


# Global event bus instance
event_bus = EventBus()

# Add default middleware
event_bus.add_middleware(LoggingMiddleware())
event_bus.add_middleware(MetricsMiddleware())

# Global event store instance
event_store = EventStore()

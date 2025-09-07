"""
Event configuration and setup for the application.
"""
import logging
from typing import Dict, Any

from src.shared.infrastructure.messaging.event_bus import EventBus, EventHandler, event_bus, event_store
from src.shared.domain.events import DomainEvent
from src.shared.domain.events import (
    ConversationStarted, ConversationCompleted, MessageAdded, AnalysisCompleted
)

logger = logging.getLogger(__name__)


class EventConfiguration:
    """Configuration class for setting up event handlers."""
    
    def __init__(self, event_bus: EventBus = None):
        self.event_bus = event_bus or event_bus
        self._handlers: Dict[str, EventHandler] = {}
        
        # Ensure event_bus is properly initialized
        if self.event_bus is None:
            from src.shared.infrastructure.messaging.event_bus import event_bus as default_event_bus
            self.event_bus = default_event_bus
    
    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register an event handler."""
        self._handlers[event_type] = handler
        self.event_bus.subscribe(event_type, handler)
        logger.info(f"Registered handler {handler.__class__.__name__} for {event_type}")
    
    def register_all_handlers(self) -> None:
        """Register all default event handlers."""
        # This method will be called to register all handlers
        # In a real application, this would be called during startup
        pass
    
    def get_handler(self, event_type: str) -> EventHandler:
        """Get a registered handler."""
        return self._handlers.get(event_type)
    
    def get_all_handlers(self) -> Dict[str, EventHandler]:
        """Get all registered handlers."""
        return self._handlers.copy()


class ConversationEventHandler(EventHandler):
    """Handler for conversation-related events."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle conversation events."""
        if isinstance(event, ConversationStarted):
            await self._handle_conversation_started(event)
        elif isinstance(event, ConversationCompleted):
            await self._handle_conversation_completed(event)
        elif isinstance(event, MessageAdded):
            await self._handle_message_added(event)
    
    async def _handle_conversation_started(self, event: ConversationStarted) -> None:
        """Handle conversation started event."""
        self.logger.info(f"Conversation {event.conversation_id} started with persona {event.persona_id}")
        
        # Store event
        await event_store.store(event)
        
        # Additional logic can be added here
        # e.g., send notifications, update metrics, etc.
    
    async def _handle_conversation_completed(self, event: ConversationCompleted) -> None:
        """Handle conversation completed event."""
        self.logger.info(
            f"Conversation {event.conversation_id} completed. "
            f"Duration: {event.duration_seconds}s, Messages: {event.message_count}"
        )
        
        # Store event
        await event_store.store(event)
        
        # Trigger analysis
        await self._trigger_analysis(event.conversation_id)
    
    async def _handle_message_added(self, event: MessageAdded) -> None:
        """Handle message added event."""
        self.logger.debug(f"Message {event.message_id} added to conversation {event.conversation_id}")
        
        # Store event
        await event_store.store(event)
    
    async def _trigger_analysis(self, conversation_id: str) -> None:
        """Trigger analysis for completed conversation."""
        try:
            # This would trigger the analysis process
            # In a real implementation, this would call the analysis service
            self.logger.info(f"Triggering analysis for conversation {conversation_id}")
            
            # For now, just log the event
            # In a real system, this would:
            # 1. Get conversation data
            # 2. Call analysis service
            # 3. Publish AnalysisCompleted event
            
        except Exception as e:
            self.logger.error(f"Failed to trigger analysis for conversation {conversation_id}: {e}")


class AnalysisEventHandler(EventHandler):
    """Handler for analysis-related events."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle analysis events."""
        if isinstance(event, AnalysisCompleted):
            await self._handle_analysis_completed(event)
    
    async def _handle_analysis_completed(self, event: AnalysisCompleted) -> None:
        """Handle analysis completed event."""
        self.logger.info(
            f"Analysis {event.analysis_id} completed for conversation {event.conversation_id}. "
            f"Score: {event.overall_score}"
        )
        
        # Store event
        await event_store.store(event)
        
        # Additional logic can be added here
        # e.g., send notifications, update dashboards, etc.


class EventBusSetup:
    """Setup class for configuring the event bus."""
    
    @staticmethod
    async def setup_event_handlers() -> EventConfiguration:
        """Setup all event handlers."""
        config = EventConfiguration()
        
        # Register conversation event handler
        conversation_handler = ConversationEventHandler()
        config.register_handler("ConversationStarted", conversation_handler)
        config.register_handler("ConversationCompleted", conversation_handler)
        config.register_handler("MessageAdded", conversation_handler)
        
        # Register analysis event handler
        analysis_handler = AnalysisEventHandler()
        config.register_handler("AnalysisCompleted", analysis_handler)
        
        logger.info("Event handlers configured successfully")
        return config
    
    @staticmethod
    async def setup_event_middleware() -> None:
        """Setup event middleware."""
        # Middleware is already added in the event_bus module
        logger.info("Event middleware configured successfully")
    
    @staticmethod
    async def setup_event_store() -> None:
        """Setup event store."""
        # Event store is already initialized in the event_bus module
        logger.info("Event store configured successfully")
    
    @staticmethod
    async def setup_all() -> EventConfiguration:
        """Setup all event-related components."""
        await EventBusSetup.setup_event_middleware()
        await EventBusSetup.setup_event_store()
        config = await EventBusSetup.setup_event_handlers()
        
        logger.info("Event bus setup completed successfully")
        return config

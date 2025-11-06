"""
Tests for event bus to improve coverage
"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.shared.infrastructure.messaging.event_bus import EventBus, InMemoryEventBus
from src.shared.domain.events import DomainEvent, MessageAdded, ConversationStarted


class TestEventBusCoverage:
    """Tests for event bus"""
    
    @pytest.fixture
    def event_bus(self):
        """Create event bus instance"""
        return InMemoryEventBus()
    
    def test_event_bus_initialization(self, event_bus):
        """Test event bus initializes correctly"""
        assert event_bus is not None
    
    @pytest.mark.asyncio
    async def test_subscribe_handler(self, event_bus):
        """Test subscribing a handler"""
        handler = AsyncMock()
        event_bus.subscribe(MessageAdded, handler)
        
        # Handler should be registered
        assert len(event_bus._handlers.get(MessageAdded.__name__, [])) > 0
    
    @pytest.mark.asyncio
    async def test_publish_calls_handler(self, event_bus):
        """Test publishing event calls handler"""
        handler = AsyncMock()
        event_bus.subscribe(MessageAdded, handler)
        
        event = MessageAdded(
            conversation_id="test",
            message_id="msg1",
            role="user",
            content="Test"
        )
        
        await event_bus.publish(event)
        
        handler.assert_called_once_with(event)
    
    @pytest.mark.asyncio
    async def test_publish_multiple_handlers(self, event_bus):
        """Test publishing to multiple handlers"""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe(MessageAdded, handler1)
        event_bus.subscribe(MessageAdded, handler2)
        
        event = MessageAdded(
            conversation_id="test",
            message_id="msg1",
            role="user",
            content="Test"
        )
        
        await event_bus.publish(event)
        
        handler1.assert_called_once()
        handler2.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_publish_with_no_handlers(self, event_bus):
        """Test publishing with no handlers doesn't crash"""
        event = ConversationStarted(
            conversation_id="test",
            persona_id="persona1"
        )
        
        # Should not raise
        await event_bus.publish(event)
    
    @pytest.mark.asyncio
    async def test_unsubscribe_handler(self, event_bus):
        """Test unsubscribing a handler"""
        handler = AsyncMock()
        event_bus.subscribe(MessageAdded, handler)
        event_bus.unsubscribe(MessageAdded, handler)
        
        event = MessageAdded(
            conversation_id="test",
            message_id="msg1",
            role="user",
            content="Test"
        )
        
        await event_bus.publish(event)
        
        # Handler should not be called
        handler.assert_not_called()
    
    def test_multiple_event_types(self, event_bus):
        """Test handling multiple event types"""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe(MessageAdded, handler1)
        event_bus.subscribe(ConversationStarted, handler2)
        
        # Both should be registered
        assert len(event_bus._handlers) >= 2
    
    @pytest.mark.asyncio
    async def test_handler_error_doesnt_stop_others(self, event_bus):
        """Test that handler error doesn't stop other handlers"""
        handler1 = AsyncMock(side_effect=Exception("Test error"))
        handler2 = AsyncMock()
        
        event_bus.subscribe(MessageAdded, handler1)
        event_bus.subscribe(MessageAdded, handler2)
        
        event = MessageAdded(
            conversation_id="test",
            message_id="msg1",
            role="user",
            content="Test"
        )
        
        # Should not raise, and handler2 should still be called
        await event_bus.publish(event)
        
        handler2.assert_called_once()


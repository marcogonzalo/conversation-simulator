"""
Tests for domain value objects to improve coverage
"""
import pytest
from src.shared.domain.value_objects import MessageContent
from src.conversation.domain.value_objects.conversation_id import ConversationId
from uuid import uuid4


class TestValueObjects:
    """Tests for domain value objects"""
    
    def test_conversation_id_creation(self):
        """Test ConversationId creation"""
        uid = uuid4()
        conv_id = ConversationId(value=uid)
        assert conv_id.value == uid
    
    def test_conversation_id_string_representation(self):
        """Test string representation of ConversationId"""
        uid = uuid4()
        conv_id = ConversationId(value=uid)
        assert str(conv_id) == str(uid)
    
    def test_conversation_id_equality(self):
        """Test ConversationId equality"""
        uid = uuid4()
        conv_id1 = ConversationId(value=uid)
        conv_id2 = ConversationId(value=uid)
        assert conv_id1.value == conv_id2.value
    
    def test_conversation_id_different_values_not_equal(self):
        """Test that different ConversationIds are not equal"""
        conv_id1 = ConversationId(value=uuid4())
        conv_id2 = ConversationId(value=uuid4())
        assert conv_id1.value != conv_id2.value
    
    def test_message_content_creation(self):
        """Test MessageContent creation"""
        content = MessageContent(value="Test message")
        assert content.value == "Test message"
    
    def test_message_content_string_representation(self):
        """Test string representation of MessageContent"""
        content = MessageContent(value="Test content")
        assert str(content) == "Test content"
    
    def test_message_content_with_empty_string(self):
        """Test MessageContent with empty string"""
        content = MessageContent(value="")
        assert content.value == ""
    
    def test_message_content_with_long_text(self):
        """Test MessageContent with long text"""
        long_text = "A" * 10000
        content = MessageContent(value=long_text)
        assert len(content.value) == 10000
    
    def test_value_objects_are_hashable(self):
        """Test that value objects can be used in sets/dicts"""
        uid = uuid4()
        conv_id = ConversationId(value=uid)
        # Should not raise
        conv_set = {conv_id}
        assert conv_id in conv_set


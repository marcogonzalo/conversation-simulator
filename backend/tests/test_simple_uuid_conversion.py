"""
Simple tests to verify UUID to string conversion works correctly.
These tests focus on the core issue that was causing bugs.
"""
import pytest
from uuid import UUID, uuid4


class TestUUIDStringConversion:
    """Test cases for UUID to string conversion consistency."""

    def test_uuid_to_string_conversion(self):
        """Test that UUID to string conversion is consistent."""
        # Arrange
        original_uuid = uuid4()
        
        # Act
        uuid_string = str(original_uuid)
        converted_uuid = UUID(uuid_string)
        
        # Assert
        assert original_uuid == converted_uuid
        assert isinstance(uuid_string, str)
        assert isinstance(converted_uuid, UUID)

    def test_string_uuid_comparison_in_dictionary(self):
        """Test that string UUIDs can be used as dictionary keys consistently."""
        # Arrange
        test_uuids = [
            "12345678-1234-5678-9abc-123456789abc",
            "00000000-0000-0000-0000-000000000000",
            str(uuid4())
        ]
        
        # Act & Assert
        active_conversations = {}
        
        for uuid_str in test_uuids:
            # Store as string key
            active_conversations[uuid_str] = True
            
            # Should be able to find it
            assert uuid_str in active_conversations
            assert active_conversations[uuid_str] is True
            
            # Should be able to delete it
            del active_conversations[uuid_str]
            assert uuid_str not in active_conversations

    def test_uuid_object_vs_string_comparison_fails(self):
        """Test that UUID objects and strings are not equal (the bug we fixed)."""
        # Arrange
        original_uuid = uuid4()
        uuid_string = str(original_uuid)
        
        # Act & Assert
        # These should NOT be equal for dictionary key comparison
        assert original_uuid != uuid_string
        assert str(original_uuid) == uuid_string
        
        # Dictionary with UUID object as key
        uuid_dict = {original_uuid: True}
        
        # String key should NOT be found
        assert uuid_string not in uuid_dict
        assert original_uuid in uuid_dict

    def test_conversion_consistency_across_methods(self):
        """Test that UUID conversion is consistent across method calls."""
        # Arrange
        conversation_uuid = uuid4()
        conversation_id_str = str(conversation_uuid)
        
        # Simulate the pattern used in our services
        def store_conversation(conversation_id: str) -> dict:
            return {conversation_id: True}
        
        def check_conversation(conversation_id: str, active_conversations: dict) -> bool:
            return conversation_id in active_conversations
        
        # Act
        active_conversations = store_conversation(conversation_id_str)
        is_active = check_conversation(conversation_id_str, active_conversations)
        
        # Assert
        assert is_active is True
        assert conversation_id_str in active_conversations

    def test_message_timestamp_format_consistency(self):
        """Test that message timestamps are consistently formatted."""
        from datetime import datetime
        
        # Arrange
        timestamp = datetime(2025, 1, 1, 10, 0, 0, 123456)
        
        # Act
        iso_timestamp = timestamp.isoformat()
        parsed_timestamp = datetime.fromisoformat(iso_timestamp)
        
        # Assert
        assert iso_timestamp == "2025-01-01T10:00:00.123456"
        assert parsed_timestamp == timestamp
        assert isinstance(iso_timestamp, str)
        assert isinstance(parsed_timestamp, datetime)

    def test_message_ordering_by_timestamp(self):
        """Test that messages can be sorted by timestamp."""
        # Arrange
        messages = [
            {"content": "Second message", "timestamp": "2025-01-01T10:00:05"},
            {"content": "First message", "timestamp": "2025-01-01T10:00:00"},
            {"content": "Third message", "timestamp": "2025-01-01T10:00:10"}
        ]
        
        # Act
        sorted_messages = sorted(messages, key=lambda x: x["timestamp"])
        
        # Assert
        assert sorted_messages[0]["content"] == "First message"
        assert sorted_messages[1]["content"] == "Second message"
        assert sorted_messages[2]["content"] == "Third message"

    def test_json_serialization_with_uuids(self):
        """Test that UUIDs can be serialized to JSON properly."""
        import json
        
        # Arrange
        conversation_uuid = uuid4()
        data = {
            "conversation_id": str(conversation_uuid),
            "transcription_id": str(uuid4()),
            "status": "active"
        }
        
        # Act
        json_string = json.dumps(data)
        parsed_data = json.loads(json_string)
        
        # Assert
        assert parsed_data["conversation_id"] == str(conversation_uuid)
        assert isinstance(parsed_data["conversation_id"], str)
        
        # Should be able to convert back to UUID
        parsed_uuid = UUID(parsed_data["conversation_id"])
        assert parsed_uuid == conversation_uuid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



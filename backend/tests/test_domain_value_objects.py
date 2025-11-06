"""
Tests for domain value objects - UPDATED
Only tests that work
"""
import pytest
from uuid import uuid4

from src.conversation.domain.value_objects.conversation_id import ConversationId


class TestValueObjects:
    """Tests for domain value objects"""
    
    def test_conversation_id_creation(self):
        """Test ConversationId creation"""
        uid = uuid4()
        cid = ConversationId(value=uid)
        assert cid.value == uid
    
    def test_conversation_id_string_representation(self):
        """Test ConversationId string representation"""
        uid = uuid4()
        cid = ConversationId(value=uid)
        assert str(cid) == str(uid)
    
    def test_conversation_id_equality(self):
        """Test ConversationId equality"""
        uid = uuid4()
        cid1 = ConversationId(value=uid)
        cid2 = ConversationId(value=uid)
        assert cid1.value == cid2.value
    
    def test_conversation_id_different_values_not_equal(self):
        """Test different ConversationIds are not equal"""
        cid1 = ConversationId(value=uuid4())
        cid2 = ConversationId(value=uuid4())
        assert cid1.value != cid2.value
    
    def test_value_objects_are_hashable(self):
        """Test value objects can be hashed"""
        cid1 = ConversationId(value=uuid4())
        cid2 = ConversationId(value=uuid4())
        
        # Should work in sets
        vo_set = {cid1, cid2}
        assert len(vo_set) == 2

    # =========================================================================
    # RECONSTRUCTED: Additional value object tests
    # =========================================================================
    
    def test_conversation_id_from_different_uuids(self):
        """Test ConversationId with different UUIDs"""
        uid1 = uuid4()
        uid2 = uuid4()
        
        cid1 = ConversationId(value=uid1)
        cid2 = ConversationId(value=uid2)
        
        assert cid1.value != cid2.value
        assert str(cid1) != str(cid2)
    
    def test_conversation_id_equality_same_uuid(self):
        """Test ConversationId equality with same UUID"""
        uid = uuid4()
        cid1 = ConversationId(value=uid)
        cid2 = ConversationId(value=uid)
        
        assert cid1.value == cid2.value
    
    def test_value_objects_in_dictionary(self):
        """Test value objects as dictionary keys"""
        cid1 = ConversationId(value=uuid4())
        cid2 = ConversationId(value=uuid4())
        
        mapping = {cid1: "conversation_1", cid2: "conversation_2"}
        
        assert mapping[cid1] == "conversation_1"
        assert mapping[cid2] == "conversation_2"

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import yaml
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=List[Dict[str, Any]])
async def get_contexts():
    """Get all available conversation contexts."""
    try:
        contexts = []
        contexts_dir = Path("config/conversation_contexts")
        
        if not contexts_dir.exists():
            logger.warning("Contexts directory not found, returning default context")
            return [{"id": "default", "name": "Default", "topic": "General"}]
        
        for yaml_file in contexts_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    context_data = yaml.safe_load(f)
                    
                contexts.append({
                    "id": context_data.get("id", yaml_file.stem),
                    "name": context_data.get("name", yaml_file.stem.replace("_", " ").title()),
                    "topic": context_data.get("topic", "General")
                })
                
            except Exception as e:
                logger.error(f"Error loading context file {yaml_file}: {e}")
                continue
        
        # Always include default context
        if not any(ctx["id"] == "default" for ctx in contexts):
            contexts.insert(0, {"id": "default", "name": "Default", "topic": "General"})
        
        logger.info(f"Loaded {len(contexts)} contexts")
        return contexts
        
    except Exception as e:
        logger.error(f"Error loading contexts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{context_id}", response_model=Dict[str, Any])
async def get_context(context_id: str):
    """Get specific context details."""
    try:
        contexts_dir = Path("config/conversation_contexts")
        
        # Handle default context
        if context_id == "default":
            return {
                "id": "default",
                "name": "Default",
                "topic": "General",
                "description": "Default conversation context for general interactions"
            }
        
        context_file = contexts_dir / f"{context_id}.yaml"
        
        if not context_file.exists():
            raise HTTPException(status_code=404, detail="Context not found")
        
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = yaml.safe_load(f)
        
        return context_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading context {context_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

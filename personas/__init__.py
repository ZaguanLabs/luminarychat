"""Persona loading system."""

import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional


class PersonalityDefinition:
    """Historical personality configuration."""
    
    def __init__(self, personality_id: str, system_prompt: str, created: int, owned_by: str = "zaguanai"):
        self.id = personality_id
        self.system_prompt = system_prompt
        self.created = created
        self.owned_by = owned_by

    def to_model_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI model format."""
        return {
            "id": self.id,
            "object": "model",
            "created": self.created,
            "owned_by": self.owned_by,
            "permission": [],
            "root": self.id,
            "parent": None
        }


def load_personas(pre_instructions: str = "") -> Dict[str, PersonalityDefinition]:
    """
    Load all personas from the personas directory.
    
    Args:
        pre_instructions: Common instructions to prepend to all persona biographies
        
    Returns:
        Dictionary mapping persona IDs to PersonalityDefinition objects
    """
    personas = {}
    personas_dir = Path(__file__).parent
    
    # Find all Python files in the personas directory (excluding __init__.py)
    for persona_file in personas_dir.glob("*.py"):
        if persona_file.name == "__init__.py":
            continue
        
        # Import the module
        module_name = f"personas.{persona_file.stem}"
        try:
            module = importlib.import_module(module_name)
            
            # Extract persona attributes
            persona_id = getattr(module, "PERSONA_ID", None)
            biography = getattr(module, "BIOGRAPHY", None)
            created = getattr(module, "CREATED", 0)
            owned_by = getattr(module, "OWNED_BY", "zaguanai")
            
            if persona_id and biography:
                system_prompt = pre_instructions + biography
                personas[persona_id] = PersonalityDefinition(
                    personality_id=persona_id,
                    system_prompt=system_prompt,
                    created=created,
                    owned_by=owned_by
                )
        except Exception as e:
            print(f"Warning: Failed to load persona from {persona_file.name}: {e}")
    
    return personas

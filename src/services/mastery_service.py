import json
import os
from typing import Dict
from src.domain.models import PlayerMastery
from src.repositories.recipe_repository import JsonRecipeRepository

class MasteryService:
    """Handles loading and saving of player mastery progression from a local JSON file."""

    def __init__(self, file_path: str, recipe_repository: JsonRecipeRepository):
        self.file_path = file_path
        self.recipe_repository = recipe_repository

    def load_mastery(self) -> Dict[str, PlayerMastery]:
        """Loads mastery levels from the local JSON file. Defaults to 0 if the file doesn't exist or is invalid."""
        recipes = self.recipe_repository.get_all()
        # Initialize default mastery levels at 0 for every supported potion
        masteries = {r.potion_item_id: PlayerMastery(r.potion_item_id, 0) for r in recipes}

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if k in masteries and isinstance(v, int):
                                m = PlayerMastery(k, v)
                                m.validate()
                                masteries[k] = m
            except Exception:
                # Silently default to 0 on corruption or error
                pass

        # Always save to synchronize default/new potions in JSON file
        self.save_all_masteries(masteries)
        return masteries

    def save_mastery(self, potion_item_id: str, level: int) -> None:
        """Saves a single potion's mastery level to the local JSON file."""
        masteries = self.load_mastery()
        if potion_item_id in masteries:
            m = PlayerMastery(potion_item_id, level)
            m.validate()
            masteries[potion_item_id] = m
            self.save_all_masteries(masteries)

    def save_all_masteries(self, masteries: Dict[str, PlayerMastery]) -> None:
        """Writes the entire dictionary of masteries back to the local JSON file."""
        if os.path.dirname(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        data = {k: m.mastery_level for k, m in masteries.items()}
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

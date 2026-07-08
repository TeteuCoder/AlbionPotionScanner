import pytest
import os
import json
from typing import List
from src.domain.models import PlayerMastery, PotionRecipe, Ingredient
from src.services.mastery_service import MasteryService

class MockRecipeRepository:
    def __init__(self, recipes: List[PotionRecipe]):
        self.recipes = recipes
    def get_all(self) -> List[PotionRecipe]:
        return self.recipes

@pytest.fixture
def mock_recipes():
    return [
        PotionRecipe(
            recipe_id="T4_POTION_HEAL",
            potion_item_id="T4_POTION_HEAL",
            potion_name="Healing Potion",
            family="Healing Potion",
            tier=4,
            enchantment_level=0,
            output_quantity=5,
            ingredients=[
                Ingredient(item_id="T4_BURDOCK", item_name="Crenellated Burdock", quantity=24, tier=4)
            ]
        ),
        PotionRecipe(
            recipe_id="T4_POTION_ENERGY",
            potion_item_id="T4_POTION_ENERGY",
            potion_name="Energy Potion",
            family="Energy Potion",
            tier=4,
            enchantment_level=0,
            output_quantity=5,
            ingredients=[
                Ingredient(item_id="T4_BURDOCK", item_name="Crenellated Burdock", quantity=12, tier=4),
                Ingredient(item_id="T4_MILK", item_name="Goat's Milk", quantity=6, tier=4)
            ]
        )
    ]

@pytest.fixture
def temp_mastery_file(tmp_path):
    return str(tmp_path / "player-mastery.json")

def test_player_mastery_validation():
    # Valid mastery
    m = PlayerMastery("T4_POTION_HEAL", 50)
    m.validate()

    # Invalid mastery values
    with pytest.raises(ValueError):
        PlayerMastery("T4_POTION_HEAL", -1).validate()
    with pytest.raises(ValueError):
        PlayerMastery("T4_POTION_HEAL", 101).validate()
    with pytest.raises(ValueError):
        PlayerMastery("", 50).validate()

def test_mastery_service_default(temp_mastery_file, mock_recipes):
    repo = MockRecipeRepository(mock_recipes)
    service = MasteryService(temp_mastery_file, repo)
    
    # File doesn't exist, should default to 0 and create the file
    masteries = service.load_mastery()
    assert len(masteries) == 2
    assert masteries["T4_POTION_HEAL"].mastery_level == 0
    assert masteries["T4_POTION_ENERGY"].mastery_level == 0
    assert os.path.exists(temp_mastery_file)

def test_mastery_service_existing(temp_mastery_file, mock_recipes):
    # Setup pre-existing file
    initial_data = {
        "T4_POTION_HEAL": 75,
        "T4_POTION_ENERGY": 30
    }
    with open(temp_mastery_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)
        
    repo = MockRecipeRepository(mock_recipes)
    service = MasteryService(temp_mastery_file, repo)
    
    masteries = service.load_mastery()
    assert masteries["T4_POTION_HEAL"].mastery_level == 75
    assert masteries["T4_POTION_ENERGY"].mastery_level == 30

def test_mastery_service_corrupted(temp_mastery_file, mock_recipes):
    # Setup corrupted/invalid file
    with open(temp_mastery_file, "w", encoding="utf-8") as f:
        f.write("{invalid json")
        
    repo = MockRecipeRepository(mock_recipes)
    service = MasteryService(temp_mastery_file, repo)
    
    # Should fall back to 0
    masteries = service.load_mastery()
    assert masteries["T4_POTION_HEAL"].mastery_level == 0
    assert masteries["T4_POTION_ENERGY"].mastery_level == 0

def test_mastery_service_save(temp_mastery_file, mock_recipes):
    repo = MockRecipeRepository(mock_recipes)
    service = MasteryService(temp_mastery_file, repo)
    
    # Load first
    service.load_mastery()
    # Save a value
    service.save_mastery("T4_POTION_HEAL", 85)
    
    # Reload and verify
    masteries = service.load_mastery()
    assert masteries["T4_POTION_HEAL"].mastery_level == 85
    assert masteries["T4_POTION_ENERGY"].mastery_level == 0

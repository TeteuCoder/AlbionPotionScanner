import json
import pytest
import os
from src.domain.models import PotionRecipe, Ingredient
from src.repositories.recipe_repository import (
    JsonRecipeRepository,
    RecipeLoadError,
    RecipeJSONError,
    RecipeValidationError
)

# Path to the actual repository recipe JSON
ACTUAL_RECIPES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "potion-recipes.json"
)

# Helper function to write temporary JSON content for testing
def write_temp_json(tmp_path, filename, content):
    file_path = tmp_path / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f)
    return str(file_path)

def test_successful_loading_actual_data():
    """Verify that the repository successfully loads the actual project recipe data."""
    assert os.path.exists(ACTUAL_RECIPES_FILE), f"Actual recipe file not found at {ACTUAL_RECIPES_FILE}"
    repo = JsonRecipeRepository(ACTUAL_RECIPES_FILE)
    
    recipes = repo.get_all()
    assert len(recipes) > 0
    assert repo.count() == len(recipes)
    
    # Check that T4_POTION_HEAL is loaded and correctly structured
    assert repo.exists("T4_POTION_HEAL")
    heal_recipe = repo.get_by_item_id("T4_POTION_HEAL")
    assert isinstance(heal_recipe, PotionRecipe)
    assert heal_recipe.recipe_id == "T4_POTION_HEAL"
    assert heal_recipe.potion_item_id == "T4_POTION_HEAL"
    assert heal_recipe.potion_name == "Healing Potion"
    assert heal_recipe.tier == 4
    assert heal_recipe.enchantment_level == 0
    assert heal_recipe.output_quantity == 5
    assert len(heal_recipe.ingredients) >= 1
    
    # Assert ingredients are loaded correctly
    assert isinstance(heal_recipe.ingredients[0], Ingredient)
    assert heal_recipe.ingredients[0].item_id == "T4_BURDOCK"
    assert heal_recipe.ingredients[0].quantity == 24
    assert heal_recipe.ingredients[0].tier == 4


def test_malformed_json(tmp_path):
    """Verify that malformed JSON raises a RecipeJSONError."""
    file_path = tmp_path / "malformed.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("[ { 'recipe_id': 'missing_closing_brackets' ")
        
    with pytest.raises(RecipeJSONError) as exc_info:
        JsonRecipeRepository(str(file_path))
    assert "Malformed JSON" in str(exc_info.value)


def test_non_existent_file():
    """Verify that a non-existent file path raises RecipeLoadError."""
    with pytest.raises(RecipeLoadError) as exc_info:
        JsonRecipeRepository("non_existent_file_path_12345.json")
    assert "Recipe file not found" in str(exc_info.value)


def test_root_not_array(tmp_path):
    """Verify that a JSON where root is not an array raises RecipeValidationError."""
    file_path = write_temp_json(tmp_path, "root_object.json", {"some_key": "some_value"})
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "must be a JSON array" in str(exc_info.value)


def test_missing_required_fields_recipe(tmp_path):
    """Verify that a missing required recipe field raises RecipeValidationError."""
    # 'potion_name' is missing
    bad_recipe = {
        "recipe_id": "T4_POTION_HEAL",
        "potion_item_id": "T4_POTION_HEAL",
        "family": "Healing Potion",
        "tier": 4,
        "enchantment_level": 0,
        "output_quantity": 5,
        "ingredients": [
            {
                "item_id": "T4_BURDOCK",
                "item_name": "Crenellated Burdock",
                "tier": 4,
                "quantity": 24
            }
        ]
    }
    file_path = write_temp_json(tmp_path, "missing_name.json", [bad_recipe])
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "missing required field" in str(exc_info.value)
    assert "potion_name" in str(exc_info.value)


def test_missing_required_fields_ingredient(tmp_path):
    """Verify that a missing required ingredient field raises RecipeValidationError."""
    # Ingredient 'quantity' is missing
    bad_recipe = {
        "recipe_id": "T4_POTION_HEAL",
        "potion_item_id": "T4_POTION_HEAL",
        "potion_name": "Healing Potion",
        "family": "Healing Potion",
        "tier": 4,
        "enchantment_level": 0,
        "output_quantity": 5,
        "ingredients": [
            {
                "item_id": "T4_BURDOCK",
                "item_name": "Crenellated Burdock"
            }
        ]
    }
    file_path = write_temp_json(tmp_path, "missing_qty.json", [bad_recipe])
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "missing required field" in str(exc_info.value)
    assert "quantity" in str(exc_info.value)


def test_recipe_validation_invalid_tier(tmp_path):
    """Verify that a tier outside the allowed range (4-8) raises RecipeValidationError."""
    bad_recipe = {
        "recipe_id": "T3_POTION_HEAL",
        "potion_item_id": "T3_POTION_HEAL",
        "potion_name": "Healing Potion",
        "family": "Healing Potion",
        "tier": 3,  # Invalid tier
        "enchantment_level": 0,
        "output_quantity": 5,
        "ingredients": [
            {
                "item_id": "T4_BURDOCK",
                "item_name": "Crenellated Burdock",
                "quantity": 24
            }
        ]
    }
    file_path = write_temp_json(tmp_path, "invalid_tier.json", [bad_recipe])
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "tier must be between 4 and 8" in str(exc_info.value) or "valid T4-T8 potion item" in str(exc_info.value)


def test_recipe_validation_self_referencing_ingredient(tmp_path):
    """Verify that an ingredient referencing the same item_id as the recipe raises RecipeValidationError."""
    bad_recipe = {
        "recipe_id": "T4_POTION_HEAL",
        "potion_item_id": "T4_POTION_HEAL",
        "potion_name": "Healing Potion",
        "family": "Healing Potion",
        "tier": 4,
        "enchantment_level": 0,
        "output_quantity": 5,
        "ingredients": [
            {
                "item_id": "T4_POTION_HEAL",  # Self-referencing
                "item_name": "Healing Potion Item",
                "quantity": 1
            }
        ]
    }
    file_path = write_temp_json(tmp_path, "self_referencing.json", [bad_recipe])
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "cannot be the same as the potion item ID" in str(exc_info.value)


def test_recipe_validation_duplicate_ingredients(tmp_path):
    """Verify that duplicate ingredients within a recipe raise RecipeValidationError."""
    bad_recipe = {
        "recipe_id": "T4_POTION_HEAL",
        "potion_item_id": "T4_POTION_HEAL",
        "potion_name": "Healing Potion",
        "family": "Healing Potion",
        "tier": 4,
        "enchantment_level": 0,
        "output_quantity": 5,
        "ingredients": [
            {
                "item_id": "T4_BURDOCK",
                "item_name": "Crenellated Burdock",
                "quantity": 24
            },
            {
                "item_id": "T4_BURDOCK",  # Duplicate item_id
                "item_name": "More Crenellated Burdock",
                "quantity": 12
            }
        ]
    }
    file_path = write_temp_json(tmp_path, "duplicate_ing.json", [bad_recipe])
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "Duplicate ingredient item_id" in str(exc_info.value)


def test_recipe_validation_recipe_id_mismatch(tmp_path):
    """Verify that recipe_id mismatch with potion_item_id raises RecipeValidationError."""
    bad_recipe = {
        "recipe_id": "T4_POTION_HEAL_MISMATCH",
        "potion_item_id": "T4_POTION_HEAL",
        "potion_name": "Healing Potion",
        "family": "Healing Potion",
        "tier": 4,
        "enchantment_level": 0,
        "output_quantity": 5,
        "ingredients": [
            {
                "item_id": "T4_BURDOCK",
                "item_name": "Crenellated Burdock",
                "quantity": 24
            }
        ]
    }
    file_path = write_temp_json(tmp_path, "mismatch.json", [bad_recipe])
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "must match potion_item_id" in str(exc_info.value)


def test_duplicate_recipe_ids_in_database(tmp_path):
    """Verify that loading duplicate recipes for the same potion item ID raises RecipeValidationError."""
    duplicate_recipes = [
        {
            "recipe_id": "T4_POTION_HEAL",
            "potion_item_id": "T4_POTION_HEAL",
            "potion_name": "Healing Potion 1",
            "family": "Healing Potion",
            "tier": 4,
            "enchantment_level": 0,
            "output_quantity": 5,
            "ingredients": [{"item_id": "T4_BURDOCK", "item_name": "Burdock", "quantity": 12}]
        },
        {
            "recipe_id": "T4_POTION_HEAL",
            "potion_item_id": "T4_POTION_HEAL",
            "potion_name": "Healing Potion 2",
            "family": "Healing Potion",
            "tier": 4,
            "enchantment_level": 0,
            "output_quantity": 5,
            "ingredients": [{"item_id": "T4_BURDOCK", "item_name": "Burdock", "quantity": 12}]
        }
    ]
    file_path = write_temp_json(tmp_path, "duplicate_recipes.json", duplicate_recipes)
    
    with pytest.raises(RecipeValidationError) as exc_info:
        JsonRecipeRepository(file_path)
    assert "Duplicate recipe found" in str(exc_info.value)


def test_get_by_item_id_exists_and_count(tmp_path):
    """Verify get_by_item_id(), exists() and count() behaviors."""
    valid_recipes = [
        {
            "recipe_id": "T4_POTION_HEAL",
            "potion_item_id": "T4_POTION_HEAL",
            "potion_name": "Healing Potion",
            "family": "Healing Potion",
            "tier": 4,
            "enchantment_level": 0,
            "output_quantity": 5,
            "ingredients": [{"item_id": "T4_BURDOCK", "item_name": "Burdock", "quantity": 12}]
        },
        {
            "recipe_id": "T6_POTION_HEAL",
            "potion_item_id": "T6_POTION_HEAL",
            "potion_name": "Major Healing Potion",
            "family": "Healing Potion",
            "tier": 6,
            "enchantment_level": 0,
            "output_quantity": 5,
            "ingredients": [{"item_id": "T6_FOXGLOVE", "item_name": "Foxglove", "quantity": 12}]
        }
    ]
    file_path = write_temp_json(tmp_path, "good_recipes.json", valid_recipes)
    repo = JsonRecipeRepository(file_path)
    
    # count()
    assert repo.count() == 2
    
    # exists()
    assert repo.exists("T4_POTION_HEAL") is True
    assert repo.exists("T6_POTION_HEAL") is True
    assert repo.exists("T8_POTION_HEAL") is False
    assert repo.exists("") is False
    assert repo.exists(None) is False
    
    # get_by_item_id() success
    r = repo.get_by_item_id("T6_POTION_HEAL")
    assert r.potion_name == "Major Healing Potion"
    
    # get_by_item_id() KeyError for missing
    with pytest.raises(KeyError):
        repo.get_by_item_id("T8_POTION_HEAL")
        
    # get_by_item_id() ValueError for empty
    with pytest.raises(ValueError):
        repo.get_by_item_id("")

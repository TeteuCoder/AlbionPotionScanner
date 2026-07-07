import json
import os
from typing import List, Dict, Optional
from src.domain.models import PotionRecipe, Ingredient

class RecipeRepositoryException(Exception):
    """Base exception for recipe repository errors."""
    pass

class RecipeLoadError(RecipeRepositoryException):
    """Raised when recipes cannot be loaded from the JSON source."""
    pass

class RecipeJSONError(RecipeLoadError):
    """Raised when the recipe JSON is malformed."""
    pass

class RecipeValidationError(RecipeLoadError):
    """Raised when a recipe fails validation."""
    pass

class JsonRecipeRepository:
    """Repository responsible for loading and exposing potion recipe data from a JSON file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._recipes: Dict[str, PotionRecipe] = {}
        self._load_recipes()

    def _load_recipes(self) -> None:
        if not os.path.exists(self.file_path):
            raise RecipeLoadError(f"Recipe file not found at: {self.file_path}")

        try:
            with open(self.file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RecipeJSONError(f"Malformed JSON in recipe file: {e}") from e
        except Exception as e:
            raise RecipeLoadError(f"Failed to read recipe file: {e}") from e

        if not isinstance(data, list):
            raise RecipeValidationError("Recipe file root must be a JSON array")

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise RecipeValidationError(f"Recipe at index {idx} must be a JSON object")

            try:
                recipe = self._deserialize_recipe(item, idx)
                recipe.validate()
            except RecipeValidationError:
                # Re-raise RecipeValidationError directly to keep context
                raise
            except KeyError as e:
                raise RecipeValidationError(f"Recipe at index {idx} is missing required field: {e}") from e
            except TypeError as e:
                raise RecipeValidationError(f"Recipe at index {idx} has invalid type: {e}") from e
            except ValueError as e:
                raise RecipeValidationError(f"Recipe at index {idx} failed validation: {e}") from e

            # Check for duplicate recipe_id / potion_item_id in the file
            if recipe.potion_item_id in self._recipes:
                raise RecipeValidationError(
                    f"Duplicate recipe found for potion_item_id '{recipe.potion_item_id}' at index {idx}"
                )
            self._recipes[recipe.potion_item_id] = recipe

    def _deserialize_recipe(self, item: dict, recipe_idx: int) -> PotionRecipe:
        # Check required fields at the recipe level
        required_recipe_fields = [
            "recipe_id", "potion_item_id", "potion_name", "family",
            "tier", "enchantment_level", "output_quantity", "ingredients"
        ]
        for field in required_recipe_fields:
            if field not in item:
                raise KeyError(field)

        ingredients_data = item["ingredients"]
        if not isinstance(ingredients_data, list):
            raise TypeError("ingredients must be a list")

        ingredients = []
        for idx, ing_item in enumerate(ingredients_data):
            if not isinstance(ing_item, dict):
                raise TypeError(f"Ingredient at index {idx} in recipe {recipe_idx} must be a JSON object")

            # Check required fields at the ingredient level
            required_ing_fields = ["item_id", "item_name", "quantity"]
            for field in required_ing_fields:
                if field not in ing_item:
                    raise KeyError(f"ingredients[{idx}].{field}")

            ingredient = Ingredient(
                item_id=ing_item["item_id"],
                item_name=ing_item["item_name"],
                quantity=ing_item["quantity"],
                tier=ing_item.get("tier")
            )
            ingredients.append(ingredient)

        return PotionRecipe(
            recipe_id=item["recipe_id"],
            potion_item_id=item["potion_item_id"],
            potion_name=item["potion_name"],
            family=item["family"],
            tier=item["tier"],
            enchantment_level=item["enchantment_level"],
            output_quantity=item["output_quantity"],
            ingredients=ingredients,
            source_reference=item.get("source_reference")
        )

    def get_all(self) -> List[PotionRecipe]:
        """Returns all loaded potion recipes."""
        return list(self._recipes.values())

    def get_by_item_id(self, item_id: str) -> PotionRecipe:
        """Retrieves a potion recipe by its item ID. Raises KeyError if not found."""
        if not item_id:
            raise ValueError("item_id cannot be empty")
        if item_id not in self._recipes:
            raise KeyError(f"Recipe with item_id '{item_id}' not found")
        return self._recipes[item_id]

    def exists(self, item_id: str) -> bool:
        """Checks if a potion recipe exists for the given item ID."""
        if not item_id:
            return False
        return item_id in self._recipes

    def count(self) -> int:
        """Returns the total number of loaded recipes."""
        return len(self._recipes)

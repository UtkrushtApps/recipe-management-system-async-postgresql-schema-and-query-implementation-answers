from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class IngredientBase(BaseModel):
    name: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    title: str
    description: Optional[str]
    instructions: Optional[str]

class RecipeCreate(RecipeBase):
    category_name: Optional[str]
    ingredient_names: List[str]

class RecipeUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    instructions: Optional[str]
    category_name: Optional[str]
    ingredient_names: Optional[List[str]]

class Recipe(RecipeBase):
    id: int
    category: Optional[Category]
    ingredients: List[Ingredient]
    created_at: datetime
    view_count: int
    class Config:
        orm_mode = True

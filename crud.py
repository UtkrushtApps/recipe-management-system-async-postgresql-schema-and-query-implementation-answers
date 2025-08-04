from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from models import Recipe, Ingredient, Category

# CREATE
async def create_recipe(session, title: str, description: str, instructions: str, category_name: str, ingredient_names: List[str]):
    # Ensure category
    category = None
    if category_name:
        category = await session.scalar(select(Category).where(Category.name == category_name))
        if not category:
            category = Category(name=category_name)
            session.add(category)
            await session.flush()

    ingredient_objs = []
    for name in ingredient_names:
        ingredient = await session.scalar(select(Ingredient).where(Ingredient.name == name))
        if not ingredient:
            ingredient = Ingredient(name=name)
            session.add(ingredient)
            await session.flush()
        ingredient_objs.append(ingredient)
    
    recipe = Recipe(
        title=title,
        description=description,
        instructions=instructions,
        category=category,
        ingredients=ingredient_objs
    )
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    return recipe

# READ
async def get_recipe_by_id(session, recipe_id: int):
    stmt = select(Recipe).where(Recipe.id == recipe_id).options(
        selectinload(Recipe.ingredients),
        selectinload(Recipe.category)
    )
    result = await session.execute(stmt)
    recipe = result.scalars().first()
    return recipe

async def list_recipes(session, skip: int = 0, limit: int = 20):
    stmt = select(Recipe).order_by(Recipe.created_at.desc()).offset(skip).limit(limit).options(
        selectinload(Recipe.ingredients),
        selectinload(Recipe.category)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def search_recipes_by_ingredient(session, ingredient_name: str, skip: int=0, limit: int=20):
    stmt = select(Recipe).join(Recipe.ingredients).where(Ingredient.name.ilike(f'%{ingredient_name}%')).options(
        selectinload(Recipe.ingredients),
        selectinload(Recipe.category)
    ).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def filter_recipes_by_category(session, category_name: str, skip: int=0, limit: int=20):
    stmt = select(Recipe).join(Recipe.category).where(Category.name.ilike(f'%{category_name}%')).options(
        selectinload(Recipe.ingredients),
        selectinload(Recipe.category)
    ).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

# UPDATE
async def update_recipe(session, recipe_id: int, title: Optional[str]=None, description: Optional[str]=None, instructions: Optional[str]=None, category_name: Optional[str]=None, ingredient_names: Optional[List[str]]=None):
    recipe = await get_recipe_by_id(session, recipe_id)
    if not recipe:
        return None

    if title:
        recipe.title = title
    if description:
        recipe.description = description
    if instructions:
        recipe.instructions = instructions
    if category_name:
        category = await session.scalar(select(Category).where(Category.name == category_name))
        if not category:
            category = Category(name=category_name)
            session.add(category)
            await session.flush()
        recipe.category = category
    if ingredient_names is not None:
        ingredient_objs = []
        for name in ingredient_names:
            ingredient = await session.scalar(select(Ingredient).where(Ingredient.name == name))
            if not ingredient:
                ingredient = Ingredient(name=name)
                session.add(ingredient)
                await session.flush()
            ingredient_objs.append(ingredient)
        recipe.ingredients = ingredient_objs
    
    await session.commit()
    await session.refresh(recipe)
    return recipe

# DELETE
async def delete_recipe(session, recipe_id: int):
    recipe = await get_recipe_by_id(session, recipe_id)
    if not recipe:
        return False
    await session.delete(recipe)
    await session.commit()
    return True

# Background: Log recipe view (simply increment view_count atomically)
async def log_recipe_view(session, recipe_id: int):
    stmt = (
        update(Recipe)
        .where(Recipe.id == recipe_id)
        .values(view_count=Recipe.view_count + 1)
    )
    await session.execute(stmt)
    await session.commit()

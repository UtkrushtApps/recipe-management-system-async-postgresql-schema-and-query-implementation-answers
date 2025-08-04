from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Table,
    Text,
    DateTime,
    Index,
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(class_registry=None)

# Association table for many-to-many between Recipes and Ingredients
recipe_ingredient_table = Table(
    'recipe_ingredient', Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_recipe_ingredient_recipe_id', 'recipe_id'),
    Index('ix_recipe_ingredient_ingredient_id', 'ingredient_id')
)

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, index=True, nullable=False)
    
    recipes = relationship('Recipe', back_populates='category', cascade='all, delete')

class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, index=True, nullable=False)
    
    recipes = relationship(
        'Recipe',
        secondary=recipe_ingredient_table,
        back_populates='ingredients'
    )

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), index=True, nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    category = relationship('Category', back_populates='recipes')
    ingredients = relationship(
        'Ingredient',
        secondary=recipe_ingredient_table,
        back_populates='recipes'
    )

    __table_args__ = (
        Index('ix_recipes_category_id', 'category_id'),
        Index('ix_recipes_title', 'title')
    )

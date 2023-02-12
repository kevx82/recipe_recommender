"""
This module defines the models for the Postgres Database
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Float

Base = declarative_base()

class Ingredients(Base):
    __tablename__ = "ingredients"
    
    id =Column(String, primary_key=True)
    name = Column(String)

class IngredientDict(Base):
    __tablename__ = "ingredient_dict"
    
    id = Column(Integer, primary_key=True)
    ingredient_id = Column(String, ForeignKey("ingredients.id"))
    name = Column(String)
    language = Column(String)
    
class Recipes(Base):
    __tablename__ = "recipes"
    
    id =Column(String, primary_key=True)
    name = Column(String)
    energy_kj = Column(Float)
    energy_kcal = Column(Float)
    fat = Column(Float)
    sat_fat = Column(Float)
    carbs = Column(Float)
    sugar = Column(Float)
    protein = Column(Float)
    salt = Column(Float)
    prep_time = Column(Integer)
    difficulty = Column(String)
    
class RecipeSteps(Base):
    __tablename__ = "recipe_steps"
    
    id =Column(String, primary_key=True)
    recipe_id = Column(String, ForeignKey("recipes.id"))
    step = Column(Integer)
    text = Column(String)
    
class RecipeLinks(Base):
    __tablename__ = "recipe_links"
    
    id =Column(String, primary_key=True)
    recipe_id = Column(String, ForeignKey("recipes.id"))
    ingredient_id = Column(String, ForeignKey("ingredients.id"))
    amount = Column(Float)
    unit = Column(String)
    
class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
class UserFavorites(Base):
    __tablename__ = "user_favorites"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(String, ForeignKey("recipes.id"))
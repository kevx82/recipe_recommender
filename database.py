import os
import json
import hashlib
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine, insert, inspect, select, func
from sqlalchemy_utils import database_exists, create_database

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

def create_hash_id(object):
    """
    This method creates a hash specifically fot the string that serves as an id.
    """
    if isinstance(object, str):
        return hashlib.shake_256(object.encode()).hexdigest(10)
    elif isinstance(object, dict):
        return hashlib.shake_256( json.dumps(object).encode()).hexdigest(10)

def create_uri_string():
    """
    Method to create uri string for the PostgresDB.
    """

    uri = "postgresql://"+ \
        f"{os.getenv('POSTGRES_USER')}:" \
        f"{os.getenv('POSTGRES_PASSWORD')}@" \
        f"{os.getenv('POSTGRES_HOST')}:" \
        f"{os.getenv('POSTGRES_PORT')}/" \
        f"{os.getenv('POSTGRES_DB')}" \

    return uri

def get_engine():
    """
    This method returns an engine for the provided database.
    """
    return create_engine(create_uri_string())

def check_database(engine):
    if not database_exists(engine.url):
        logging.warning("No database found!")
        create_database(engine.url)
        logging.warning("Database created!")

def check_table(engine, table):
    """
    Method that creates a tables if it does not exist.
    """
    check_database(engine)
    if not inspect(engine).has_table(table.__tablename__):
        table.__table__.create(bind=engine, checkfirst=True)
        logging.info(f"Table {table.__tablename__} created!")
        
def check_id(engine, table, id):
    """
    This method checks if the id of the object is already in the table.
    """
    stmt = (
        select(table).where(table.id == id)
    )
        
    with engine.connect() as conn:
        output = conn.execute(stmt).all()

    return True if len(output) > 0 else False

def get_id_by_name(engine, table, name):
    """
    This method gets the id in a table by name 
    """
    stmt = (
        select(table.id).where(table.name == name)
    )
    with engine.connect() as conn:
        name_id = conn.execute(stmt).fetchone()[0]
    
    return name_id

def get_name_by_id(enginge, table, name):
    """
    This methods gets the name of an ingredient by the id.
    """
    stmt = (
        select(table.name).where(table.id == name)
    )
    with enginge.connect() as conn:
        id_name = conn.execute(stmt).fetchone()[0]
        
    return id_name

def insert_data(engine, table, values):
    """
    This method inserts the object values into the table.
    """
    with engine.connect() as conn:
        conn.execute(
            insert(table), values
        )
        conn.commit()
    
def fill_table(engine, table, values_list):
    """
    This method takes care of the filling of the table. 
    """
    check_table(engine, table)
    for values in values_list:
        if not check_id(engine, table, values['id']):
            insert_data(engine, table, values)
            
def get_recipe_ingredients(engine, table1, table2, calc):
    """
    This methods returns all ingredient for each recipe.
    """
    if calc =='count':
        stmt = (
            select(
                table1.recipe_id.label('id'),
                table2.name,
                func.count(table2.name).label('count')
            ).join(
                table2,
                table1.ingredient_id == table2.id
            ).group_by(
                table1.recipe_id,
                table2.name
            ).order_by(
                table1.recipe_id
            )
        )
    elif calc == 'amount':
        stmt = (
            select(
                table1.recipe_id.label('id'),
                table2.name,
                table1.amount
                ).join(
                    table2,
                    table1.ingredient_id == table2.id
                    )
                )
    
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()
    return result

def get_recipe_info(engine, table, recipe_ids):
    """
    This method queries the recipe information that contains the recipe id, name, nutritions, prep_time, difficulty.
    """
    stmt = (
        select(table).where(table.id.in_(recipe_ids))
    )
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()
    return result

def get_full_recipe_info(engine, table1, table2, table3, recipe_ids):
    """
    This method queries the full information of the desired recipes ids that contains teh following:
        * recipe id
        * name
        * ingredient
        * amount
        * unit
        * preparation time
        * unit
    """
    stmt = (
        select(
            table2.id,
            table2.name,
            table3.name.label('ingredient'),
            table1.amount,
            table1.unit,
            table2.prep_time,
            table2.difficulty
        ).join(
            table2,
            table1.recipe_id == table2.id
        ).join(
            table3,
            table1.ingredient_id == table3.id
        ).where(table2.id.in_(recipe_ids))
    )
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()
    return result

def get_all_ingredients(engine, table):
    """
    This method returns a list of all avaiable ingredients for the recipe.
    """
    stmt = (
        select(table.name)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()
    return result

def get_recipe_steps(engine, table, recipe_ids):
    """
    This method queries all steps of the provided recipes.
    """
    stmt = (
        select(table.recipe_id, table.step, table.text).where(table.recipe_id.in_(recipe_ids))
    )
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()
    return result

def query_user_favorites(engine, table, user_id):
    """
    This method queries all favorite recipe ids of a user.
    """
    stmt = (
        select(table.recipe_id).where(table.user_id == user_id)
    )   
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()
    return result

import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics.pairwise import cosine_similarity

import database as db
from db_models import *


class RecipeRecommender:
    
    def __init__(self, user_name) -> None:
        self.engine = db.get_engine()
        self.user_name = user_name
        
        self.user_id = self.get_user_id()
        self.ingredients = self.query_ingredients()
        self.fav_recipe_ids = self.query_favorites()
        
        self.rec_recipes = None
        self.recipe_steps = None
        
    def query_ingredients(self):
        ingredients = pd.DataFrame(db.get_all_ingredients(self.engine, Ingredients))
        return  ingredients.name.to_list()

    def query_recipe_ingredients(self, calc='amount', pivot=True):
        rec_ingr = pd.DataFrame(db.get_recipe_ingredients(self.engine, RecipeLinks, Ingredients, calc=calc))
        
        if pivot:
            rec_ingr = rec_ingr.pivot(index='id', columns='name', values=calc)
            rec_ingr = rec_ingr.fillna(0)
        
        return rec_ingr 

    def query_recipes(self, recipe_ids, full_info=True, duplicates=True):
        recipes = pd.DataFrame(db.get_recipe_info(self.engine, Recipes, recipe_ids))
        
        if duplicates:
            recipes = recipes.drop_duplicates(subset='name')
        if full_info:
            recipes = recipes.drop(columns=['name', 'difficulty'])
        
        return recipes
    
    def get_user_id(self):
        try:
            user_id = db.get_id_by_name(self.engine, Users, self.user_name)
        except:
            db.check_table(self.engine, Users)
            db.insert_data(self.engine, Users, {'name': self.user_name})
        finally:
            user_id = db.get_id_by_name(self.engine, Users, self.user_name)
        
        return user_id
        
    def add_favorites(self, recipe_ids):
        user_recipes = [{'user_id': self.user_id, 'recipe_id': recipe_id} for recipe_id in recipe_ids]
        for user_dict in user_recipes: 
            user_dict['id'] = db.create_hash_id(user_dict)
        
        db.fill_table(self.engine, UserFavorites, user_recipes)

    def query_favorites(self):
        fav_recipe_ids = db.query_user_favorites(self.engine, UserFavorites, self.user_id)
        fav_recipe_ids = [recipe_id[0] for recipe_id in fav_recipe_ids]
        return fav_recipe_ids
    
    def get_favorites(self):
        return pd.DataFrame(db.get_full_recipe_info(self.engine, RecipeLinks, Recipes, Ingredients, self.fav_recipe_ids))

    def get_fitting_recipes(self, rec_ingr, ingr_names, ingr_choice, min_fit=3):
        ingr_choice_df = pd.DataFrame({ingr: [1] for ingr in ingr_choice}, columns=ingr_names, index=['ingr_choice']).fillna(0)
        dot = np.dot(ingr_choice_df.to_numpy(), rec_ingr.to_numpy().transpose())
        dot_df = pd.DataFrame(dot[0], columns=['dot'], index=rec_ingr.index)
        print(f"Fitting recipes based on ingredient choice:\n{dot_df['dot'].value_counts()}")
        
        recipe_ids = dot_df[dot_df['dot'] >= min_fit].index.to_list()
        
        return recipe_ids    

    def create_feature_matrix(self, rec_ingr, recipe_ids):
        recipe_ids = recipe_ids + self.fav_recipe_ids
        ingr_matrix_df = rec_ingr.loc[rec_ingr.index.isin(recipe_ids)].reset_index()
        recipe_matrix = self.query_recipes(recipe_ids)
        
        return recipe_matrix.merge(ingr_matrix_df, on='id', how='left')

    def calculate_similarity(self, rec_ingr_cos, recipe_ids):
        feature_df = self.create_feature_matrix(rec_ingr_cos, recipe_ids).set_index('id')
        
        scaler = RobustScaler()
        data = scaler.fit_transform(feature_df)
        data = pd.DataFrame(data, columns=feature_df.columns, index=feature_df.index)
        
        cos_matrix = cosine_similarity(data)
        cos_df = pd.DataFrame(cos_matrix, columns=feature_df.index, index=feature_df.index)
        
        return cos_df

    def recommend_recipe(self, ingr_choice, top_k=5):
        rec_ingr_dot = self.query_recipe_ingredients(calc='count')
        ingr_names = rec_ingr_dot.columns
        
        print(f"ingredients of choice: {ingr_choice}")
        recipe_ids = self.get_fitting_recipes(rec_ingr_dot, ingr_names, ingr_choice)
        rec_ingr_cos = self.query_recipe_ingredients()
        
        cos_df = self.calculate_similarity(rec_ingr_cos, recipe_ids)
        top_recipe_ids = cos_df.loc[~cos_df.columns.isin(self.fav_recipe_ids),cos_df.columns.isin(self.fav_recipe_ids)].sum(axis=1).sort_values(ascending=False).index[:top_k].to_list()
        print(f"top recipe ids: {top_recipe_ids}")
        
        self.rec_recipes = pd.DataFrame(db.get_full_recipe_info(self.engine, RecipeLinks, Recipes, Ingredients, top_recipe_ids))
        self.recipe_steps = pd.DataFrame(db.get_recipe_steps(self.engine, RecipeSteps, top_recipe_ids))
        print(self.recipe_steps)
        #print(self.rec_recipes.groupby(['id', 'name']).agg({'ingredient': lambda x: ', '.join(sorted(x))}))

if __name__ == '__main__': 
    np.random.seed(23)
    
    # test ingredients
    ingr_choice = ['Tomato', 'Halloumi', 'Chicken', 'Potatoes', 'Lettuce']
    rr = RecipeRecommender('testuser')
    print(f"user_id: {rr.user_id}")
    #fav_recipe_ids = ['6312GB', '6500GB', '6853GB', '7146GB', '7496GB']
    #rr.add_favorites(fav_recipe_ids)
    print(f"{rr.fav_recipe_ids}")
    #rr.recommend_recipe(ingr_choice)
    #rr.add_favorite(rr.fav_recipe_ids[0])
        
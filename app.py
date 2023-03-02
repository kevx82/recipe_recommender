import re

from PIL import Image
import streamlit as st

from recommender import RecipeRecommender

size = (250, 180)
broccolove = Image.open(f'streamlit/sad_broccoli.png')
broccolove = broccolove.resize((390, 400), Image.ANTIALIAS)

with open('streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)   
    
    
rr = RecipeRecommender('testuser')

if 'show_recipe' not in st.session_state:
    st.session_state['show_recipe'] = False
if 'recommend' not in st.session_state:
    st.session_state['recommend'] = False
if 'rec_recipes' not in st.session_state:
    st.session_state['rec_recipes'] = None
if 'recipe_steps' not in st.session_state:
    st.session_state['recipe_steps'] = None
if 'chosen_recipe' not in st.session_state:
    st.session_state['chosen_recipe'] = None
    

with st.sidebar:
    st.sidebar.title("Choose ")
    st.sidebar.subheader("What ingredients you want to use?")
    
def get_simple_name(name):
    simple_name = re.sub(r'[^A-Za-z0-9]+', r'', name)
    simple_name = re.sub(r' ', r'_', simple_name)
    return simple_name

def get_image(country, recipe_id, name, size):
    try:
        image = Image.open(f'data/img/{country}/{recipe_id}_{name}.jpg')
    except:
        image = Image.open(f'streamlit/default_menu.png')
        
    image = image.resize(size, Image.Resampling.LANCZOS)
    
    return image

def show_recipe():
    with tab1:
        recipe_df = st.session_state['rec_recipes']
        steps_df = st.session_state['recipe_steps']
        id = st.session_state['chosen_recipe']
        
        recipe = recipe_df[recipe_df['id'] == id].copy()
        steps = steps_df.loc[steps_df['recipe_id'] == recipe['id'].unique()[0], 'text'].to_list()
        
        recipe_id = re.sub(r'[^\d]+', '', recipe['id'].unique()[0])
        country = re.sub(r'[\d]+', '', recipe['id'].unique()[0])
        file_name = get_simple_name(recipe['name'].unique()[0])
        
        # image of recipe page
        image = get_image(country, recipe_id, file_name, size=(700,450))
        st.image(image)
        
        # name of the recipe
        recipe_name = recipe['name'].unique()[0]
        st.markdown(f"**{recipe_name}**")
        
        with st.container():
            col1, col2 = st.columns([5,1], gap="small")
            with col1:
                # preparation time and difficulty of the recipe
                prep_time = recipe['prep_time'].unique()[0]
                difficulty = recipe['difficulty'].unique()[0]
                st.markdown(f"Time: {prep_time} min.  |  Difficulty: {difficulty}")
            with col2:
                favorite = st.button("favorite")
                if favorite:
                    rr.add_favorites([id])
        
        with st.container():
            col3, col4 = st.columns([1,2], gap="small")
            with col3:
                # table with ingredients and amounts
                recipe['unit_amount'] = recipe['amount'].apply(lambda x: round(x)).astype(str) + ' ' + recipe['unit']
                styled = recipe[['ingredient', 'unit_amount']].style.hide(axis='index')
                styled.hide(axis='columns')
                st.write(styled.to_html(), unsafe_allow_html=True)
            with col4:
                for i, step in enumerate(steps):
                    st.write(f"{i + 1}: {step}")

def print_favorites(recipe, top_n):
    with tab2:
        recipe_id = re.sub(r'[^\d]+', '', recipe['id'].unique()[0])
        country = re.sub(r'[\d]+', '', recipe['id'].unique()[0])
        name = get_simple_name(recipe['name'].unique()[0])
        
        with st.container():
            col1, col2, col3 = st.columns([1,3, 1], gap="small")
            with col1:
                image = get_image(country, recipe_id, name, size=size)
                st.image(image)
            with col2:
                name = recipe['name'].unique()[0]
                prep_time = recipe['prep_time'].unique()[0]
                difficulty = recipe['difficulty'].unique()[0]
                st.markdown(f"**{name}**")
                st.markdown(f"Time: {prep_time} min.  |  Difficulty: {difficulty}")
            with col3:
                favorite_btn = col3.button(f"show recipe #{top_n + 1}")
                if favorite_btn:
                    st.session_state['show_recipe'] = True
                    st.session_state['recommend'] = False
                    st.session_state['chosen_recipe'] = recipe['id'].unique()[0]
                    #rr.fav_recipe_ids.add_favorite(recipe_id)        

def print_recipes(recipe, top_n):
    with tab1:
        recipe_id = re.sub(r'[^\d]+', '', recipe['id'].unique()[0])
        country = re.sub(r'[\d]+', '', recipe['id'].unique()[0])
        name = get_simple_name(recipe['name'].unique()[0])
        
        with st.container():
            col1, col2, col3 = st.columns([1,3, 1], gap="small")
            with col1:
                image = get_image(country, recipe_id, name, size=size)
                st.image(image)
            with col2:
                name = recipe['name'].unique()[0]
                prep_time = recipe['prep_time'].unique()[0]
                difficulty = recipe['difficulty'].unique()[0]
                st.markdown(f"**{name}**")
                st.markdown(f"Time: {prep_time} min.  |  Difficulty: {difficulty}")
            with col3:
                recipe_btn = col3.button(f"eat recipe #{top_n + 1}")
                if recipe_btn:
                    st.session_state['show_recipe'] = True
                    st.session_state['recommend'] = False
                    st.session_state['chosen_recipe'] = recipe['id'].unique()[0]
                    #rr.fav_recipe_ids.add_favorite(recipe_id)

def get_recipes():
    button = st.sidebar.button(label='recommend recipes')
    if button:
        st.session_state['recommend'] = True
        st.session_state['show_recipe'] = False
        
ingr1 = st.sidebar.selectbox(label='1', label_visibility='collapsed', options=rr.ingredients, index=rr.ingredients.index('Tomato'))
ingr2 = st.sidebar.selectbox(label='2', label_visibility='collapsed', options=rr.ingredients, index=rr.ingredients.index('Potato'))
ingr3 = st.sidebar.selectbox(label='3', label_visibility='collapsed', options=rr.ingredients, index=rr.ingredients.index('Beef'))
ingr4 = st.sidebar.selectbox(label='4', label_visibility='collapsed', options=rr.ingredients, index=rr.ingredients.index('Water'))
ingr5 = st.sidebar.selectbox(label='5', label_visibility='collapsed', options=rr.ingredients, index=rr.ingredients.index('Lettuce'))
top_k = st.sidebar.slider("# of recommendations", 1, 10, value=5)

tab1, tab2 = st.tabs(['Recommender', 'Favorites'])
with tab1:
    st.title("Recipe Recommender")
with tab2:
    fav_recipes = rr.get_favorites()
    for top_n, fav_id in enumerate(fav_recipes['id'].unique()):
        print_favorites(fav_recipes[fav_recipes['id'] == fav_id], top_n)
    
get_recipes()

if st.session_state['show_recipe']:
    show_recipe()
elif st.session_state['recommend']:
    rr.recommend_recipe([ingr1, ingr2, ingr3, ingr4, ingr5], top_k=top_k)
    st.session_state['rec_recipes'] = rr.rec_recipes
    st.session_state['recipe_steps'] = rr.recipe_steps
    if len(rr.rec_recipes) > 0:
        recipe_ids = list(rr.rec_recipes['id'].unique())
        for top_n, r_id in enumerate(recipe_ids):
            print_recipes(rr.rec_recipes[rr.rec_recipes['id'] == r_id], top_n)
    else:
        with tab1:
            st.image(broccolove)
            st.markdown("**No recipes found for this combination. Please try a few others!**")
else:
    print("MAINNNNNESDFGEGewsfihifsiudkfjhsduoijk")
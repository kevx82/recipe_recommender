# recipe_recommender
The app recommends recipes based on the input ingredients and favourite recipes.

## Database

The database used for this project is PostgreSQL. The following image shows the schema of the database.

![database_schena](example/database_schema.png)

### Tables

__Ingredients__

The `ingredients` table contains all ingredient used for the recipes.

* `id` (string): hash generated id based on the ingredient nane
* `name` (string): name of the ingredient

__Recipes__

The `recipes` table contains the basic information of all recipes.

* `id` (string): given id for the recipe combined of incremented number and origin
* `name` (string): title of the recipe
* `energy_kj` (float): kilo joule per portion for the recipe
* `energy_kcal` (float): kilo calories per portion for the recipe
* `fat` (float): amount of fat per portion for the recipe
* `sat_fat` (float): amount of saturated fat per portion for the recipe
* `carbs` (float): amount of carbs per portion for the recipe
* `sugar` (float): amount of sugar per portion for the recipe
* `protein` (float): amount of protein per portion for the recipe
* `salt` (float): amount of salt per portion for the recipe
* `preparation` (integer): time to prepare the recipe
* `difficulty` (string): difficulty to prepare to the recipe

__RecipeLinks__

The `recipe_links` table links the recipes to the ingredients with amounts and units.

* `id` (string): hash generated id based on the `recipe_id`, `ingredient_id`, `amount` and `unit`
* `recipe_id` (string): id of the recipe
* `ingredient_id` (string): id of the ingredient
* `amount` (float): amount of the ingredient
* `unit` (string): unit of the amount

__RecipeSteps__

The `recipe_steps` table contains the steps to prepare each recipe.

* `id` (string): hash generated id based on the `recipe_id`, `step` and `text`.
* `recipe_id` (string): id of the recipe
* `step` (integer): number of the step
* `text` (string): text of the current step

__Users__

The `users` table contains all the user information.

* `id` (integer): increasing integer starting from 1
* `name` (string): name of the user

__UserFavorites__

The `user_favorites` table contains all favorite recipes of the users.

* `id` (string): hash generated id based on the `user_id` and `recipe_id`
* `user_id` (string): id of the user
* `recipe_id` (string): id of the recipe

### Data

This repository is currently not providing any recipe data for the database.


## Application

### Running the App

The recipe recommender is using streamlit to run the application on a web browser. To run the  \
application the following command needs to be executed:

```bash
streamlit run app.py
```

If the command is not executed inside the folder of the app, please add the path (`~/path/app.py`)

### Using the APP

The following animation shows the basic functionality of the recipe recommender.

![recipe_recommender](example/usage.gif)


1. Choose the ingredients you want to use
2. Set the amount of recommended recipes you want to receive
3. Push __recommend recipes__ to get recommendations
4. Select a recipe and push __eat recipe__ to see full information
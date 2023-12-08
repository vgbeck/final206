import json
import requests

def merge_category_files(files):
    result = []
    for file in files:
        with open(file, "r") as add_file:
            result.append(json.load(add_file))
        
    with open("meals.json", "w") as meals_file:
        json.dump(result, meals_file, indent = 4)

def create_meals_by_id():
    with open('meals.json', 'r') as file:
        meal_data = json.load(file)
    
    all_meals = []

    for category in meal_data:
        for meals, data in category.items():
            for meal in data:
                meal_id = meal['idMeal']
                meal_by_id_API = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}')
                meal_by_id_data = meal_by_id_API.json()
                all_meals.append(meal_by_id_data)
    with open("meals_by_id.json", "w") as write_file:
        json.dump(all_meals, write_file, indent = 4)

def get_num_ingredients(filename):
    with open(filename, "r") as file:
        data = json.load(file)

    ingredients_count = {}
    for category in data:
        for meal in category['meals']:
            meal_id = meal['idMeal']
            count = 0
            i = 1

            while True:
                ingredient_key = f"strIngredient{i}"
                if ingredient_key in meal and meal[ingredient_key]:
                    count += 1
                    i += 1
                else:
                    break

            ingredients_count[meal_id] = count
    
    return ingredients_count

def get_num_meals_per_category_list(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    
    meals_count_list = []

    for item in data:
        if 'meals' in item:
            meals_count = len(item['meals'])
            meals_count_list.append(meals_count)
    
    return meals_count_list

def get_category_id_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    
    category_id_dict = {}

    for category in data['categories']:
        category_name = category['strCategory']
        category_id = category['idCategory']
        category_id_dict[category_name] = category_id

    return category_id_dict

def get_category_id_list(filename):
    category_id_dict = get_category_id_dict("categories.json")

    with open(filename, 'r') as file:
        data = json.load(file)
    
    category_ids = []

    for category_data in data:
        for meal_entry in category_data['meals']:
            category_name = meal_entry['strCategory']
            category_id = category_id_dict.get(category_name)
            category_ids.append(category_id)
    
    return category_ids


def count_data_points(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    count = 0 

    for item in data:
        if 'meals' in item:
            count += len(item['meals'])
    
    return count

# print(count_data_points("meals.json"))
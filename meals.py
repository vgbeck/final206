import requests
import sqlite3
import json
import os
from helper_functions import *



def set_up(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn

def create_meals_table(cur, conn):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS meals (id INTEGER PRIMARY KEY, meal_id INTEGER, name TEXT, category_id INTEGER, num_ingredients INTEGER)
        """
    )
    conn.commit()

def create_categories_table(cur, conn):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, category_name TEXT, num_meals INTEGER)
        """
    )
    conn.commit()

def add_meal(filename, cur, conn):
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename)))
    file_data = f.read()
    f.close()
    data = json.loads(file_data)

    try:
        cur.execute(
            """
            SELECT id FROM meals ORDER BY id DESC LIMIT 1 
            """
        )
        start = cur.fetchone()[0]

    except:
        start = -1
    
    temp = start + 1

    #create a list of tuples to enter into the database below
    meal_data = []
    id = 0
    for item in data:
        for meal in item['meals']:
            meal_id = meal['idMeal']
            name = meal['strMeal']
            category_id = get_category_id_list(filename)[id]
            num_ingredients = get_num_ingredients(filename)[meal_id]
            meal_data.append((int(id), int(meal_id), name, int(category_id), int(num_ingredients)))
            id += 1
            
    # insert the data by 25
    for i in range(temp, temp + 25):
        if i < len(meal_data):
            cur.execute(
                """
                INSERT OR IGNORE INTO meals (id, meal_id, name, category_id, num_ingredients) VALUES (?,?,?,?,?)
                """, 
                meal_data[i]
            )
            conn.commit()

    conn.commit()

# No need to insert the data by 25 because there are only 14 rows
def add_category(filename, cur, conn):
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename)))
    file_data = f.read()
    f.close()
    data = json.loads(file_data)
    i = 0

    for info_list in data.values():
        for meal in info_list:
            id = meal['idCategory']
            category_name = meal['strCategory']
            meals_count_list = get_num_meals_per_category_list('meals.json')
            num_meals = meals_count_list[i]
            i += 1

            cur.execute(
                """
                INSERT OR IGNORE INTO categories (id, category_name, num_meals) VALUES (?,?,?)
                """,
                (int(id), category_name, int(num_meals))
            )

    conn.commit()
    

#SETUP 

# Request from the categories API
categories_API = requests.get("https://www.themealdb.com/api/json/v1/1/categories.php")
data = categories_API.text
categories = json.loads(data)
with open("categories.json", "w") as write_file_1:
    json.dump(categories, write_file_1, indent = 4)

category_name_list = []
for str, all_data in categories.items():
    for category in all_data:
        category_name = category["strCategory"]
        category_name_list.append(category_name)


## Look-up meals by category -- requesting from each of these APIs and will combine them into one file
files_list = []
for name in category_name_list:
    meals_in_category_API = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?c={name}")
    meal_data = meals_in_category_API.text
    meals = json.loads(meal_data)
    with open(f"meals_{name}.json", "w") as write_file_2:
        json.dump(meals, write_file_2, indent = 4)
        files_list.append(f"meals_{name}.json")



## Combining each category json file into a file, meals.json, with all of the meals
merge_category_files(files_list)
## Checking if meals_by_id.json already exists in the directory. I don't want to create it multiple times if it already 
## exists because it takes over a minute to run.
if not os.path.exists('meals_by_id.json'):
    create_meals_by_id()

cur, conn = set_up('food_friends.db')
create_meals_table(cur, conn)
create_categories_table(cur, conn)

add_meal("meals_by_id.json", cur, conn)
add_category("categories.json", cur, conn)
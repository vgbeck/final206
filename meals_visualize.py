import matplotlib.pyplot as plt
import csv
from meals import * 

def calculate_averages(cur):
    cur.execute(
        """
        SELECT categories.category_name, AVG(meals.num_ingredients)
        FROM meals
        JOIN categories
        ON meals.category_id = categories.id
        GROUP BY categories.category_name
        """
    )
    avg_data = cur.fetchall()
    return avg_data

def create_barchart(avg_data):
    categories, averages = zip(*avg_data)

    colors = ['lightpink', 'purple']
    color_array = []
    for i in range(len(categories)):
        color_index = i % len(colors)
        color_array.append(colors[color_index])

    plt.figure(figsize = (10,6))
    plt.bar(categories, averages, color = color_array)
    plt.xlabel('Category')
    plt.ylabel('Average Number of Ingredients')
    plt.title('Average Number of Ingredients Per Category')
    plt.xticks(rotation = 45)
    plt.tight_layout()
    
    plt.show()

def count_meal_types(cur):
    categories = ['Vegetarian', 'Vegan']
    counts = {'Vegetarian': 0, 'Vegan': 0, 'Other': 0}

    for category in categories:
        cur.execute(
            """
            SELECT COUNT(*) FROM meals
            JOIN categories ON meals.category_id = categories.id
            WHERE categories.category_name = ?
            """, 
            (category,)
        )
        count = cur.fetchone()[0]
        counts[category] = count
    
    vegetarian, vegan = categories

    cur.execute(
        """
        SELECT COUNT(*) FROM meals
        WHERE category_id NOT IN (
            SELECT id FROM categories WHERE category_name IN (?, ?)
        )
        """,
        (vegetarian, vegan)
    )
    counts['Other'] = cur.fetchone()[0]

    return counts

def create_pie_chart(meal_counts):
    labels = meal_counts.keys()
    counts = meal_counts.values()

    slice_colors = ['lightcoral', 'orchid', 'lightblue']

    plt.figure(figsize = (8,8))
    plt.pie(counts, labels = labels, autopct = '%1.1f%%', colors = slice_colors)
    plt.axis('equal')
    plt.title('Inclusivity of Common Dietary Restrictions')
    plt.show()

def file_contains_header(filename, header):
    if not os.path.exists(filename):
        return False
    with open(filename, 'r', newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if row == header:
                return True
    return False

def write_averages_to_csv(avg_data, filename):
    header = ['Category', 'Average Number of Ingredients']
    if not file_contains_header(filename, header):
        with open(filename, 'a', newline = '') as csvfile:
            csvwriter = csv.writer(csvfile)

            csvwriter.writerow([])
            csvwriter.writerow(header)

            for row in avg_data:
                csvwriter.writerow(row)

def write_num_meals_type_to_csv(meal_types, filename):
    header = ['Meal Type', 'Number of Meals']
    if not file_contains_header(filename, header):
        with open(filename, 'a', newline = '') as csvfile:
            csvwriter = csv.writer(csvfile)

            csvwriter.writerow([])
            csvwriter.writerow(header)

            for meal_type, count in meal_types.items():
                csvwriter.writerow([meal_type, count])
    

cur, conn = set_up('food_friends.db')

avg_data = calculate_averages(cur)
meal_counts = count_meal_types(cur)
create_barchart(avg_data)
create_pie_chart(meal_counts)
write_averages_to_csv(avg_data, 'output.csv')
write_num_meals_type_to_csv(meal_counts, 'output.csv')

conn.close()
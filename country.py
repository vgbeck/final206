import requests
import json
import os
import sqlite3
import ssl
import pprint
import matplotlib.pyplot as plt


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def create_country_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS country (id INTEGER PRIMARY KEY, country_id TEXT, name TEXT)")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn.commit()

def add_country(filename, cur, conn):
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename)))
    file_data = f.read()
    f.close()
    data = json.loads(file_data)

    #finds the max id from the table
    try:
        cur.execute(
            """
                SELECT id 
                FROM country
                WHERE id = (SELECT MAX(id) FROM country)
            """
        )
        start = cur.fetchone()
        start = start[0]
    except:
        start = 0

    temp = start

    #adds the next 25 items
    for item in data[start:start+25]:
        id = temp
        temp += 1
        country_id = item["countryCode"]
        name = item["name"]
        cur.execute("INSERT OR IGNORE INTO country (id, country_id, name) VALUES (?,?,?)", (id, country_id, name, ))
        conn.commit()

def create_holiday_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS holiday (id INTEGER PRIMARY KEY, country_id INTEGER, date TEXT, local_name TEXT, name TEXT)")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn.commit()

def add_holiday(cur, conn, holiday_count):
    #finds the max id from the table
    try:
        cur.execute(
            """
                SELECT id 
                FROM holiday
                WHERE id = (SELECT MAX(id) FROM holiday)
            """
        )
        start = cur.fetchone()
        start = start[0]
    except:
        start = 0

    #this is the max id to be saved at
    holiday_count = start

    #these are the four countries to be graphed
    four_countries = ["US", "IE", "AU", "FR"]
    #loops through each country
    for item in four_countries:
        #creates a json
        json_name = item + ".json"

        #finds the country_id that matches across both tables
        cur.execute(
        f"""
            SELECT id
            FROM country
            WHERE country_id = (?)

        """, (item,)
        )
        res = cur.fetchone()
        res2 = 0

        #if the data from the country with the matching country_id has been loaded in (res is not none)
        if not(res == None):
            #this returns if data from that country has been added to the holiday table
            cur.execute(
            f"""
                SELECT id
                FROM holiday
                WHERE country_id = (?)

            """, (res[0],)
            )
            res2 = cur.fetchone()
        #if the country data is ready to be loaded and is not already in holidays
        if not(res == None) and (res2 == None):
            #call to the country's API
            response_country = requests.get('https://date.nager.at/api/v3/PublicHolidays/2024/' + str(item), verify=False)
            data2 = json.loads(response_country.text)
            #write to the country's json file
            with open(json_name, "w") as write_file:
                json.dump(data2, write_file, indent=4)
        
            f = open(json_name)
            data = json.load(f)
            #load the json data
            #this does not need a 25 limit because there are never more than 25 holidays in each country json
            for holiday in data:
                #loop through each holiday in the json and save identifiers
                date = str(holiday["date"])
                local_name = str(holiday["localName"])
                name = str(holiday["name"])

                #load holiday data into database
                cur.execute("INSERT OR IGNORE INTO holiday (id, country_id, date, local_name, name) VALUES (?,?,?,?,?)", (holiday_count, res[0], date, local_name, name))
                holiday_count += 1
                conn.commit()
    

def main():
    cur, conn = setUpDatabase('food_friends.db')
    create_country_table(cur, conn)
    response_API = requests.get('https://date.nager.at/api/v3/AvailableCountries', verify = False)
    data = json.loads(response_API.text)
    with open("country.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
    add_country("country.json", cur, conn)
    holiday_count = 1
    create_holiday_table(cur, conn)
    add_holiday(cur, conn, holiday_count)

    
        


if __name__ == "__main__":
    main()
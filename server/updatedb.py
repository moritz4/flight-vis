#!/usr/bin/python

# This script updates a database of flight positions.
# This script should be run periodlically

import argparse
import sqlite3
import requests

airports = [ "LHR", "LGW", "MAN", "STN", "LTN", "EDI", "BHX", "BRS", "GLA", "BFS", "NCL", "LPL", "LBA", "EMA", "LCY"]

# Get database path from command line
parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()

# Get flight data from API
url = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"}
params = {"estimated": 1, "to": ",".join(airports)}
res = requests.get(url = url, headers = headers, params = params)

if(res.status_code != 200):
    print("Failed to get flight data. Server responded with status code " + str(res.status_code))
    print(res.text)
    exit(1)

# parse data and remove the full_count and version keys
data = res.json()
data.pop("full_count")
data.pop("version")

# Now turn the data into a list of tuples
flights = [(k, *v)for k, v in data.items()]

# Open database
con = sqlite3.connect(args.path)
cur = con.cursor()

# Create positions table if it doesn't exist
cur.execute(
    '''CREATE TABLE IF NOT EXISTS positions (
            id TEXT, 
            SSR TEXT,
            latitude REAL,
            longitude REAL,
            heading INTEGER,
            altitude INTEGER,
            speed INTEGER,
            squawk TEXT,
            tower_code TEXT,
            model TEXT,
            registration TEXT,
            time INTEGER,
            origin TEXT,
            destination TEXT,
            iata TEXT,
            on_ground INTEGER,
            vertical_speed INTEGER,
            icao TEXT,
            unkown REAL,
            airline TEXT)
    ''')

# write data to database
cur.executemany("INSERT INTO positions VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", flights)

# Commit changes and close database
con.commit()
con.close()

print("Wrote " + str(len(flights)) + " rows to database")
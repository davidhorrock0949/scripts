#!/usr/bin/python3
import sqlite3
import os
import csv
import argparse
import re
from datetime import datetime, timedelta
import time

DB_NAME = "data.db"


def setup_database():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE data
             (column1 TEXT, column2 TEXT, column3 TEXT)''')
        conn.commit()
        conn.close()


def import_csv_to_database(filename):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute("INSERT INTO data VALUES (?, ?, ?)", (row[0], row[1], row[2]))
    conn.commit()
    conn.close()


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def convert_to_bytes(size_str):
    size_str = size_str.lower()
    size = float(re.match(r"^\d+(\.\d+)?", size_str).group())
    if 'kb' in size_str:
        return int(size * 1024)
    elif 'mb' in size_str:
        return int(size * 1024**2)
    elif 'gb' in size_str:
        return int(size * 1024**3)
    elif 'tb' in size_str:
        return int(size * 1024**4)
    else:
        return int(size)


def search_database(search_texts=None, before_date=None, after_date=None, days_old=None, sort_by=None, truncate=None, minsize=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = 'SELECT * FROM data WHERE 1=1'
    params = []

    if search_texts:
        search_texts = search_texts.split(',')
        for text in search_texts:
            query += ' AND column1 LIKE ?'
            params.append('%' + text.strip() + '%')

    if before_date:
        query += ' AND column3 <= ?'
        params.append(before_date)

    if after_date:
        query += ' AND column3 >= ?'
        params.append(after_date)

    if days_old:
        start_date = (datetime.today() - timedelta(days=int(days_old))).strftime('%Y-%m-%d')
        query += ' AND column3 >= ?'
        params.append(start_date)

    if minsize:
        min_bytes = convert_to_bytes(minsize)
        query += ' AND CAST(column2 AS INTEGER) >= ?'
        params.append(min_bytes)
        print(f"Minimum size: {minsize} -> {min_bytes} bytes")  # This is for debugging.

    max_valid_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    query += ' AND column3 <= ?'
    params.append(max_valid_date)

    query += ' AND CAST(column2 AS INTEGER) >= 0'

    if sort_by == "filename":
        query += ' ORDER BY column1'
    elif sort_by == "size":
        query += ' ORDER BY CAST(column2 AS INTEGER)'
    elif sort_by == "date":
        query += ' ORDER BY column3'

    query += ' LIMIT 500000'

    start_time = time.time()
    cursor.execute(query, params)
    results = cursor.fetchall()
    end_time = time.time()

    for row in results:
        filename = row[0]
        if truncate is not None:
            if len(filename) > truncate:
                filename = '...' + filename[-truncate:]
        formatted_size = format_size(int(row[1]))
        if truncate is not None:
                print(f"{filename:<{truncate + 5}} {formatted_size:<15} {row[2]}")
        else:
                print(f"{filename} {formatted_size:<15} {row[2]}")

    conn.close()

    search_duration = end_time - start_time
    print("\nSearch took {:.4f} seconds.".format(search_duration))
    print("Found {} results.".format(len(results)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search a database using specific criteria.')
#    parser.add_argument('-s', '--search', required=False, help='Text to search for in the database.')
#    parser.add_argument('-s', '--search', nargs='*', required=False, help='List of keywords to search for in the database.')
    parser.add_argument('-s', '--search', type=str, required=False, help='Comma-separated list of keywords to search for in the database.')
    parser.add_argument('--before', type=str, help='Filter results before this date (YYYY-MM-DD format).')
    parser.add_argument('--after', type=str, help='Filter results after this date (YYYY-MM-DD format).')
    parser.add_argument('--daysold', type=int, help='Show items newer than x days.')
    parser.add_argument('--sort', choices=['filename', 'size', 'date'], help='Sort results by filename, size, or date.')
    parser.add_argument('-t', '--truncate', type=int, nargs='?', const=50, help='Truncate the filename to the specified width. Defaults to 50 characters if no number is provided.')
    parser.add_argument('--minsize', type=str, help='Filter results to a minimum size. Accepts values in bytes, or with "kb", "mb", or "gb" suffixes.')

    args = parser.parse_args()

    setup_database()

    if not os.path.exists(DB_NAME):
        filename = input("Enter the path to the CSV file: ")
        import_csv_to_database(filename)
    
    search_database(args.search, args.before, args.after, args.daysold, args.sort, args.truncate, args.minsize)

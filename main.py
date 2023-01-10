#!/usr/bin/env python3

from db import Database
import argparse

def main():
    parser = argparse.ArgumentParser(
                        prog = 'Badger-NG',
                        description = 'Makespace Badger')
    parser.add_argument('--init', action='store_true')
    parser.add_argument('-d', '--database', help='sqlite3 database file', required=True)

    args = parser.parse_args()

    if not args.init:
        # Check if the DB file exists
        try:
            db = Database(f'file:{args.database}?mode=ro')
            db.close()
        except Exception as e:
            print("Error:", e)
            print("If you need to create a new one, use --init")
            exit(1)

    db = Database(args.database)
    if args.init:
        try:
            db.initialise()
        except Exception as e:
            print("Error:", e)
            print("Perhaps the database is already initialised")
            exit(1)

if __name__ == "__main__":
    main()

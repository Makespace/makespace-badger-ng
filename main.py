#!/usr/bin/env python3

from db import Database
import argparse

def enrol(db, args):
    tag = bytes(args.tag, 'utf-8')
    print(f'Enrolling tag: {tag}, name: {args.name}, contact: {args.contact}')
    db.insert(tag, args.name, args.contact)

def update(db, args):
    tag = bytes(args.tag, 'utf-8')
    print(f'Updating tag: {tag}, name: {args.name}, contact: {args.contact}')
    db.update(tag, args.name, args.contact)

def lookup(db, args):
    tag = bytes(args.tag, 'utf-8')
    name, contact = db.lookup(tag)
    print(f'Lookup tag:{tag}, name:{name}, contact:{contact}')

def main():
    parser = argparse.ArgumentParser(
                        prog='badger-ng',
                        description='Makespace Badger')
    parser.add_argument('--init', action='store_true')
    parser.add_argument('-d', '--database', help='sqlite3 database file', required=True)

    subparsers = parser.add_subparsers(title="Sub-commands")

    # Common arguments for tag handling commands
    tag_cmd_parser = argparse.ArgumentParser(description="parent parser for tag commands")
    tag_cmd_parser.add_argument('tag', help='Tag ID')
    tag_cmd_parser.add_argument('name', help='Tag owner name')
    tag_cmd_parser.add_argument('contact', help='Tag owner contact')

    enrol_parser = subparsers.add_parser('enrol', add_help=False,
                                         parents=[tag_cmd_parser],
                                         help='Add a tag to the database')
    enrol_parser.set_defaults(func=enrol)

    update_parser = subparsers.add_parser('update', add_help=False,
                                          parents=[tag_cmd_parser],
                                          help='Update a tag in the database')
    update_parser.set_defaults(func=update)

    lookup_parser = subparsers.add_parser('lookup', add_help=False,
                                          help='Look up a tag in the database')
    lookup_parser.add_argument('tag', help='Tag ID')
    lookup_parser.set_defaults(func=lookup)

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

    try:
        args.func(db, args)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from db import Database
from label import Label
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

def label(db, args):
    lbl = Label(args.lines, args.dpi, (args.width_mm, args.height_mm))

    img = lbl.image()
    if args.out is None:
        img.show()
    else:
        img.save(args.out)

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

    label_parser = subparsers.add_parser('label', add_help=False,
                                          help='Generate a label image')
    label_parser.add_argument('--dpi', help='Image DPI', type=int, default=300)
    label_parser.add_argument('-w', '--width_mm', help='Label width (mm)', type=int, default=89)
    label_parser.add_argument('-h', '--height_mm', help='Label height (mm)', type=int, default=36)
    label_parser.add_argument('--out', help='Output filename (default: preview)', default=None)
    label_parser.add_argument('lines', help='Text lines to put on label', nargs='*')
    label_parser.set_defaults(func=label)

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

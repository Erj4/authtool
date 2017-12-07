#!/usr/bin/python3
import argparse
import os
import sys
import pyotp

SEPARATOR = ':'

parser = argparse.ArgumentParser(prog="authtool",
                                 description="A Simple 2 Factor Authenticator")


def run(args):
    if hasattr(args, "name"):
        if ":" in args.name or "\n" in args.name:
            print("Invalid authenticator name!", file=sys.stderr)
            print("Please use a name that does not contain '"
                  + SEPARATOR + "' or '\\n'",
                  file=sys.stderr)
            return
    if args.file:
        file_name = args.file
    else:
        file_name = os.path.join(os.path.expanduser("~"),".authtool")
    if args.mode != "init" and not os.path.isfile(file_name):
        print("The file '" + file_name + "' does not exist!", file=sys.stderr)
        print("Run 'authtool init' first to create it", file=sys.stderr)
        return
    args.func(args, file_name)


def init_authenticator(args, file_name):
    if os.path.isfile(file_name):
        print("File already exists. Skipping file creation.")
    else:
        print("Creating file...")
        open(file_name, mode='x').close()
    print("Setting file read/edit permissions...")
    os.chmod(file_name, 0o660)


def add_authenticator(args, file_name):
    with open(file_name, mode='a+') as f:
        for line in f:
            if line.split(SEPARATOR)[0] == args.name:
                print("An authenticator with that name already exists!",
                      file=sys.stderr)
                print("The new authenticator has NOT been saved.",
                      file=sys.stderr)
                return
        f.write(args.name + ":" + args.key + "\n")


def print_authenticator(args, file_name):
    with open(file_name, mode='r') as f:
        key = None
        for line in f:
            line = line.strip()
            if line.split(SEPARATOR)[0] == args.name:
                key = line.split(SEPARATOR)[1]
        if not key:
            print("No authenticator with that name was found!",
                  file=sys.stderr)
            return
        print("Password: " + pyotp.TOTP(key).now())
        if args.key:
            print("Authenticator key: " + key)


def list_authenticators(args, file_name):
    firstLine = True
    with open(file_name, mode='r') as f:
        for line in f:
            if line == "\n":
                continue
            if not firstLine and (args.passwords or args.keys):
                print()
            line = line.strip()
            if args.passwords or args.keys:
                print("Name: ", end="")
            print(line.split(SEPARATOR)[0])
            if args.passwords:
                print("Password: "
                      + pyotp.TOTP(line.split(SEPARATOR)[1]).now())
            if args.keys:
                print("Authenticator key: " + line.split(SEPARATOR)[1])


def remove_authenticator(args, file_name):
    print("Are you sure you want to delete " + args.name + "? (y/N)",
          file=sys.stderr, end=" ")
    sure = (input().lower() == "y")
    if not sure:
        print("Cancelling")
        return
    with open(file_name, mode='r') as f:
        lines = f.readlines()
    with open(file_name, mode='w') as f:
        for line in lines:
            if line.split(SEPARATOR)[0] == args.name:
                print("Deleting " + args.name)
                continue
            else:
                f.write(line)


subparsers = parser.add_subparsers(dest="mode")

parser_add = subparsers.add_parser("add")
parser_add.add_argument("name",
                        help="Name of new authenticator (for human reading)")
parser_add.add_argument("key", help="Key to save for generating passwords")
parser_add.add_argument("-f", "--file", help="File to edit")
parser_add.set_defaults(func=add_authenticator)

parser_remove = subparsers.add_parser("remove")
parser_remove.add_argument("name",
                           help="Name of authenticator to remove")
parser_remove.add_argument("-f", "--file", help="File to edit")
parser_remove.set_defaults(func=remove_authenticator)

parser_print = subparsers.add_parser("print")
parser_print.add_argument("name")
parser_print.add_argument("-k", "--key",
                          help="Print saved key", action="store_true")
parser_print.add_argument("-f", "--file", help="File to read")
parser_print.set_defaults(func=print_authenticator)

parser_list = subparsers.add_parser("list")
parser_list.add_argument("-p", "--passwords",
                         help="Print TOTP passwords", action="store_true")
parser_list.add_argument("-k", "--keys",
                         help="Print saved keys", action="store_true")
parser_list.add_argument("-f", "--file", help="File to read")
parser_list.set_defaults(func=list_authenticators)

parser_init = subparsers.add_parser("init")
parser_init.add_argument("-f", "--file", help="File to create")
parser_init.set_defaults(func=init_authenticator)


args, extras = parser.parse_known_args()
if args.mode is None:
    parser_list.parse_args(extras, namespace=args)
run(args)

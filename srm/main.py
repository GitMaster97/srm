#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


"""
Module for working with Remover in console
"""


import argparse
import logging
import os
import sys
import pytoml

from srm.remove_policy import RemovePolicy
from srm.logger_tools import setup_console_logger, setup_file_logger
from srm.config_operations import(
    create_config,
    load_config,
    update_config,
    cat_config
)
from srm.wastebasket_manager import WasteBasketManager
from srm.exit_codes import ExitCode
from srm.move_error import MoveError
from srm.timedelta_parser import parse_timedelta


CONFIG_PATH = os.path.expanduser("~/.smart_rm_config.json")
WASTEBASKET_PATH = os.path.expanduser("~/Trash")

POLICY = RemovePolicy.SIZE
STORAGE_TIME = "30 days, 0:0:0"
MAX_SIZE = 32.0

def srm_process(func):
    def srm_process_wrapper():
        exit_code = ExitCode.SUCCESS
        try:
            func()
        except MoveError as exception:
            logging.error(exception)
            exit_code = ExitCode.MOVE_ERROR
        except KeyboardInterrupt as exception:
            exit_code = ExitCode.SIGINT
        except pytoml.core.TomlError as exception:
            logging.error("Cannot parse like toml.")
            exit_code = ExitCode.INCORRECT_CONFIG_FORMAT

        sys.exit(exit_code)

    return srm_process_wrapper


def create_parser():
    """
    Returns an ArgumentParser with arguments added
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--restore", action="store_true",
                        help="Action for work")
    parser.add_argument("--silent", action="store_true",
                        help="Don't show the actions performed")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulates action to be performed on console")
    parser.add_argument("--force", action="store_true",
                        help="Ignore non-existent files and arguments")
    parser.add_argument("--wastebasket-path", default=WASTEBASKET_PATH,
                        help="Sets the path to the wastebasket")

    parser.add_argument("-r", "--rmdir", action="store_true",
                        help="Remove directories")
    parser.add_argument("--regex", action="store_true",
                        help="Remove nodes by regular expression")

    parser.add_argument("--content", action="store_true",
                        help="Shows the wastebasket contents")
    parser.add_argument("--short", action="store_true",
                       help="Shows the wastebasket contents")
    parser.add_argument("--in-lines", action="store_true",
                        help="Shows the wastebasket contents")
    parser.add_argument("--clear", action="store_true",
                        help="Clear WasteBasket")

    parser.add_argument("--update-config", action="store_true",
                        help="Update config file")
    parser.add_argument("--create-config", action="store_true",
                        help="Create config file")
    parser.add_argument("--config", default=CONFIG_PATH,
                        help="Specifies the path to the config file in json format")
    parser.add_argument("--cat-config", action="store_true",
                        help="Displays the contents of the configuration file")

    parser.add_argument("--cleaning-policy", choices={RemovePolicy.SIZE, RemovePolicy.TIME},
                        default=POLICY,
                        help="Sets the clean policy")
    parser.add_argument("--max-size", type=float, default=MAX_SIZE,
                        help="Sets the maximum volume value for the wastebasket (in GB)")
    parser.add_argument("--storage-time", default=STORAGE_TIME,
                        help="Determines how long the files should \
                        be stored from the time of deletion. Format: 2017-08-09T23:59:03")

    parser.add_argument("--log", help="Specifies the path to log file.")

    parser.add_argument("paths", nargs='*', help="Name of the file(s) or directory(ies) to restore")

    return parser


def get_args_from_console(args):
    """
    Returns arguments from the stdin.
    """
    return {
        "cleaning_policy": args.cleaning_policy,
        "clear": args.clear,
        "content": args.content,
        "dry_run": args.dry_run,
        "force": args.force,
        "in_lines": args.in_lines,
        "max_size": args.max_size,
        "regex": args.regex,
        "restore": args.restore,
        "rmdir": args.rmdir,
        "short": args.short,
        "silent": args.silent,
        "storage_time": args.storage_time,
        "wastebasket_path": args.wastebasket_path
    }


def get_merged_args(args):
    """
    Returns the dictionary of arguments.
    If not specified determines from the config file.
    """
    config_dict = load_config(args.config)

    args_dict = {
        "cleaning_policy": args.cleaning_policy,
        "clear": args.clear,
        "content": args.content,
        "dry_run": args.dry_run,
        "force": args.force,
        "in_lines": args.in_lines,
        "max_size": args.max_size,
        "regex": args.regex,
        "restore": args.restore,
        "rmdir": args.rmdir,
        "short": args.short,
        "silent": args.silent,
        "storage_time": args.storage_time,
        "wastebasket_path": args.wastebasket_path
    }

    for arg, value in args_dict.iteritems():
        if not value:
            args_dict[arg] = config_dict[arg]

    if args_dict["cleaning_policy"] == POLICY:
        args_dict["cleaning_policy"] = config_dict["cleaning_policy"]

    if args_dict["storage_time"] == STORAGE_TIME:
        args_dict["storage_time"] = config_dict["storage_time"]

    if args_dict["max_size"] == MAX_SIZE:
        args_dict["max_size"] = config_dict["max_size"]

    return args_dict


def get_wastebasket_args(args):
    """
    Return a dictionary of WastebasketManager fields.
    """
    return {
        "dry_run": args["dry_run"],
        "force": args["force"],
        "rmdir": args["rmdir"],
        "max_size": args["max_size"],
        "storage_time": args["storage_time"],
        "wastebasket_path": args["wastebasket_path"]
    }


@srm_process
def main():
    """
    Module entry point
    """
    args = create_parser().parse_args()

    if not os.path.exists(CONFIG_PATH):
        create_config(args.config, get_args_from_console(args))

    if args.create_config:
        create_config(args.config, get_args_from_console(args))
    if args.update_config:
        update_config(args.config, get_args_from_console(args))

    working_args_dict = get_merged_args(args)
    if not working_args_dict["silent"]:
        setup_console_logger()
    if args.log:
        setup_file_logger(filename=args.log)

    if args.cat_config:
        cat_config(args.config)

    wastebasket_args = get_wastebasket_args(working_args_dict)
    wastebasket_args["storage_time"] = parse_timedelta(wastebasket_args["storage_time"])
    wastebasket = WasteBasketManager(**wastebasket_args)

    if working_args_dict["cleaning_policy"] == RemovePolicy.SIZE:
        if wastebasket.clear_by_size_policy():
            logging.info("WasteBasket was cleaned.")
    elif working_args_dict["cleaning_policy"] == RemovePolicy.TIME:
        auto_removed_files = wastebasket.clear_by_time_policy()
        for filename in auto_removed_files:
            msg = "Auto-removed {name}".format(name=filename)
            logging.info(msg)

    if working_args_dict["content"]:
        short = working_args_dict["short"]
        in_lines = working_args_dict["in_lines"]
        
        separator = "\n" if in_lines else ", "
        
        wastebasket_content = unicode(wastebasket.trashinfo)
        if short:
            wastebasket_content = separator.join(wastebasket.trashinfo.iterkeys())
        
        logging.info(wastebasket_content)
        
    if working_args_dict["clear"]:
        wastebasket.clear()

    if working_args_dict["restore"]:
        moved_files = wastebasket.restore(*args.paths)
        for src, dst in moved_files:
            msg = 'Restored from "{src}" to "{dst}".'.format(src=src, dst=dst)
            logging.info(msg)
    else:
        if working_args_dict["regex"] and args.paths:
            moved_files = wastebasket.remove_regex(args.paths[0], search_dirs=True)
            for src, dst in moved_files:
                msg = 'Removed from "{src}" to "{dst}".'.format(src=src, dst=dst)
                logging.info(msg)
        else:
            moved_files = wastebasket.remove(*args.paths)
            for src, dst in moved_files:
                msg = 'Removed from "{src}" to "{dst}".'.format(src=src, dst=dst)
                logging.info(msg)

if __name__ == "__main__":
    main()

#!/usr/bin/python
# JTemplator
# GitHub: https://github.com/derifgig/jtemplator
#

import argparse
import logging
import os
import yaml

VERSION = "v0.1"
DEFAULT_LOGGING_LEVEL = logging.INFO



def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f"Jinja2 Templator {VERSION}"
    )
    parser.add_argument("-c", "--config",
                        required=True,
                        help="Config file in YML format")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        required=False,
                        default=False,
                        help="verbose mode")
    return parser.parse_args()


def check_file_readable(filename):
    try:
        result = os.path.exists(filename)
        if not result:
            logging.error("File not found: %s " % filename)
        else:
            logging.debug("File present: %s " % filename)
        return result
    except IOError:
        logging.error("File not accessible: %s " % filename)
        return False


def validate_config_file(config_file):

    cf_name = 'name'
    cf_template = 'template'
    cf_output_path = 'output_path'
    cf_output_file_name_template = 'output_file_name_template'
    cf_input_data_file_yaml = 'input_data_file_yaml'
    cf_mode = 'mode'

    required_fields = [
        cf_name,
        cf_template,
        cf_output_path,
        cf_output_file_name_template,
        cf_input_data_file_yaml,
        cf_mode
    ]

    logging.debug("Validation config file: %s" % config_file)

    if not check_file_readable(config_file):
        return False

    try:
        stream = open(config_file, 'r')
    except IOError:
        logging.error("Error reading from file: %s" % config_file)
        return False

    try:
        config_data = yaml.safe_load(stream)

        logging.debug('Data type in config file recognized: %s' % type(config_data))
        is_items_valid = True
        for item_config in config_data:
            if cf_name in item_config:
                logging.debug('Validation config item: %s' % item_config[cf_name])

            # checking for required fields
            is_required_fields = True
            for i in required_fields:
                if i not in item_config:
                    logging.error('Required field not found in config file: %s' % i)
                    is_required_fields = False

            if is_required_fields:
                logging.info('Item is valid: %s' % item_config[cf_name])
            else:
                is_items_valid = False
        #
        if not is_items_valid:
            logging.error('Can not continue with this config file')

    except yaml.YAMLError as exc:
        logging.error('Error parsing YAML data from config file')
        return False


def main():
    args = parse_arguments()
    logging_level = DEFAULT_LOGGING_LEVEL
    if args.verbose:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s")

    logging.info("Config file: %s" % args.config)
    if not validate_config_file(args.config):
        return 1

    logging.info("Finished")


if __name__ == "__main__":
    main()

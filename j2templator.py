#!/usr/bin/python
import argparse
import logging
import os
import yaml
import jinja2

APP = "j2templator"
GITHUBURL = "https://github.com/derifgig/j2templator"
VERSION = "v0.1"
DEFAULT_LOGGING_LEVEL = logging.INFO
CFG = []

# field names in YAML config file
cf_name = 'name'
cf_template = 'template'
cf_output_path = 'output_path'
cf_output_path_create = 'output_path_create'
cf_output_file_name_template = 'output_file_name_template'
cf_input_data_file_yaml = 'input_data_file_yaml'
cf_mode = 'mode'


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    magenta = "\x1b[35;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(message)s"

    FORMATS = {
        logging.DEBUG: yellow + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: magenta + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
# end of class CustomFormatter


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f"{APP} {VERSION} {GITHUBURL}"
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


def check_file_exist(filename, is_problem=True):
    try:
        result = os.path.exists(filename)
        if not result and is_problem:
            logger.error("  File not found: %s " % filename)
        else:
            logger.debug("  File present: %s " % filename)
        return result
    except IOError:
        logger.error("  File not accessible: %s " % filename)
        return False


def validate_config_file(config_file):

    required_fields = [
        cf_template,
        cf_output_path,
        cf_output_file_name_template,
        cf_input_data_file_yaml,
    ]
    
    mode_available_values = [
        'all',
        'one'
    ]

    mode_available_values = [
        'all',
        'one'
    ]

    logger.debug("Validation config file: %s" % config_file)

    if not check_file_exist(config_file):
        return False

    try:
        stream = open(config_file, 'r')
    except IOError:
        logger.error("Error reading from file: %s" % config_file)
        return False

    try:
        config_data = yaml.safe_load(stream)

        logger.debug('Data type in config file recognized: %s' % type(config_data))
        is_items_valid = True

        for item_index in range(len(config_data)):
            item_config = config_data[item_index]
            item_name = item_config[cf_name] if cf_name in item_config else ''
            item_prefix = 'check [%s] (%s)' % (item_index, item_name)

            logger.debug('%s : Validation config item' % item_prefix)

            # checking for required fields
            is_required_fields = True
            for i in required_fields:
                if i not in item_config:
                    logger.error('%s : No required field: [%s]' % (item_prefix, i))
                    is_required_fields = False

            if is_required_fields:
                logger.debug('%s : Item is valid' % item_prefix)

            else:
                is_items_valid = False

            # add default values
            if cf_name not in item_config:
                item_config[cf_name] = ''

            if cf_mode not in item_config:
                item_config[cf_mode] = 'all'

            if cf_output_path_create not in item_config:
                item_config[cf_output_path_create] = False

            # add new item to work
            CFG.append(item_config)

        #
        if not is_items_valid:
            logger.error('Can not continue with this config file')
            return False

    except yaml.YAMLError as exc:
        logger.error('Error parsing YAML data from config file')
        return False

    # normal final of procedure
    return True


def doit():

    if len(CFG) == 0:
        logger.debug('Length of CFG is zero. Nothing to do')
        return False

    for item_index in range(len(CFG)):
        item = CFG[item_index]
        item_prefix = 'work [%s] (%s)' % (item_index, item[cf_name])
        logger.info('%s : Started. Mode: %s Output path: %s' % (
            item_prefix,
            item[cf_mode],
            item[cf_output_path])
        )

        if not check_file_exist(item[cf_template],False):
            logger.error('%s : Template file not found: %s' % (item_prefix,item[cf_template]))
            continue

        try:
            with open(item[cf_template]) as f:
                j2_template = jinja2.Template(f.read())
        finally:
            f.close()


        # data
        content_data_file = open(item[cf_input_data_file_yaml], 'r')
        content_data = yaml.safe_load(content_data_file)

        # Checking for existing OUTPUT directory
        try:
            result = os.path.isdir(item[cf_output_path])
            if not result:
                if item[cf_output_path_create]:
                    logger.info('%s : Creation directory: %s' % (item_prefix, item[cf_output_path]))
                    os.makedirs(item[cf_output_path], exist_ok=True)
                else:
                    logger.error('%s : Output directory not found: %s' % (item_prefix, item[cf_output_path]))
                    continue
        except IOError:
            logger.error('%s : Output directory checking error: %s' % (item_prefix, item[cf_output_path]))
            return False

        # Working ...
        match item[cf_mode]:
            case 'all':
                output_file_name = item[cf_output_path]+'/'+item[cf_output_file_name_template]
                # render, and save the results to file
                logger.info('%s : Output file: %s' % (item_prefix, output_file_name))

                try:
                    with open(output_file_name, "w") as fh:
                        fh.write(j2_template.render(content=content_data))
                except IOError:
                    logger.error('%s : Writing file IOError : %s' % (item_prefix, output_file_name))
                    continue
                finally:
                    fh.close()

            case 'one':

                logger.debug('Data type of content: %s' % type(content_data))

                for data_index in range(len(content_data)):
                    item_content = content_data[data_index]

                    j2_template_output_file = jinja2.Template(item[cf_output_file_name_template])
                    output_file_name = j2_template_output_file.render(item=item_content)
                    output_file_name = item[cf_output_path]+'/'+output_file_name

                    # checking for existing files, it's no problem
                    if check_file_exist(output_file_name, False):
                        logger.info('%s : Overwriting output file: %s' % (item_prefix, output_file_name))
                    else:
                        logger.info('%s : Output file: %s' % (item_prefix, output_file_name))

                    try:
                        with open(output_file_name, "w") as fh:
                            fh.write(j2_template.render(content=item_content))
                    except IOError:
                        logger.error('%s : Writing file IOError : %s' % (item_prefix, output_file_name))
                        continue
                    finally:
                        fh.close()
            case _:
                logging.error('')

        # end of match
        logger.info('%s : Done' % item_prefix)
    return True


def main():

    args = parse_arguments()
    logger.info('Started '+APP+' '+VERSION + ' '+GITHUBURL)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Config file: %s" % args.config)
    if not validate_config_file(args.config):
        return 1

    #
    if not doit():
        return 1
    #
    logger.info("Finished")


# Define global items
logger = logging.getLogger(APP)
logging_level = DEFAULT_LOGGING_LEVEL
logger.setLevel(logging_level)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import logging
import os
import shlex
import sys

import jinja2
import yaml

APP = "j2templator"
GITHUBURL = "https://github.com/derifgig/j2templator"
VERSION = "v0.6"
DEFAULT_LOGGING_LEVEL = logging.INFO

# field names in YAML config file
cf_name = "name"
cf_template = "template"
cf_check_ignore_file_absent = "check_ignore_file_absent"
cf_output_path = "output_path"
cf_output_path_create = "output_path_create"
cf_output_file_name_template = "output_file_name_template"
cf_output_file_mode = "output_file_mode"
cf_input_data_file = "input_data_file"
cf_input_data_type = "input_data_type"
cf_additional_data_file = "additional_data_file"
cf_additional_data = "additional_data"
cf_mode = "mode"


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    magenta = "\x1b[35;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(message)s"

    FORMATS = {
        logging.DEBUG: yellow + fmt + reset,
        logging.INFO: grey + fmt + reset,
        logging.WARNING: magenta + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# end of class CustomFormatter


def parse_arguments():
    parser = argparse.ArgumentParser(description=f"{APP} {VERSION} {GITHUBURL}")
    parser.add_argument(
        "-c", "--config", required=True, help="Config file in YML format"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        required=False,
        default=False,
        help="Debug mode",
    )
    parser.add_argument(
        "-k",
        "--check",
        action="store_true",
        required=False,
        default=False,
        help="Only check config, no more",
    )
    return parser.parse_args()


def check_config_file(config_file):

    required_fields = [
        cf_template,
        cf_output_path,
        cf_output_file_name_template,
        cf_input_data_file,
    ]

    files = [
        cf_template,
        cf_input_data_file,
        cf_additional_data_file,
    ]

    mode_available_values = ["all", "one"]

    input_data_type = ["yml", "txt"]

    logger.debug("Validation config file: %s" % config_file)

    if not os.path.exists(config_file):
        logger.error(f"Config file not found: {config_file}")
        return []

    try:
        with open(config_file, "r") as stream:
            config_data = yaml.safe_load(stream)
    except IOError:
        logger.error("Error reading from file: %s" % config_file)
        return []

    if config_data is None:
        logger.error("Config file is empty: %s" % config_file)
        return []

    logger.debug("Data type in config file recognized: %s" % type(config_data))
    is_items_valid = True
    validated_items = []

    for item_index, item_config in enumerate(config_data):
        item_name = item_config.get(cf_name, "")
        item_prefix = "check [%s] (%s)" % (item_index, item_name)

        logger.debug("%s : Checking config item" % item_prefix)

        # checking for required fields
        is_required_fields = True
        for i in required_fields:
            if i not in item_config:
                logger.error("%s : No required field: [%s]" % (item_prefix, i))
                is_required_fields = False

        if is_required_fields:
            logger.debug("%s : All required fields presents." % item_prefix)
        else:
            is_items_valid = False

        check_ignore_file_absent = item_config.get(cf_check_ignore_file_absent, False)

        if check_ignore_file_absent:
            logger.warning("%s : Absent files will be ignored" % item_prefix)

        source_files_exist = True
        for i in files:
            if i in item_config:
                if not os.path.exists(item_config[i]):

                    if check_ignore_file_absent:
                        logger.warning(
                            "%s : Source file not found: [%s]"
                            % (item_prefix, item_config[i])
                        )
                    else:
                        logger.error(
                            "%s : Source file not found: [%s]"
                            % (item_prefix, item_config[i])
                        )
                        source_files_exist = False

        if not source_files_exist:
            logger.error("%s : SKIPPED" % (item_prefix))
            continue

        # add default values
        if cf_name not in item_config:
            item_config[cf_name] = ""

        if cf_mode not in item_config:
            item_config[cf_mode] = "all"
        else:
            if item_config[cf_mode] not in mode_available_values:
                logger.error(
                    "%s : Unknown mode [%s]" % (item_prefix, item_config[cf_mode])
                )
                logger.error("%s : SKIPPED" % (item_prefix))
                continue

        # Default data type - yml
        if cf_input_data_type not in item_config:
            item_config[cf_input_data_type] = "yml"
        else:
            if item_config[cf_input_data_type] not in input_data_type:
                logger.error(
                    "%s : Unknown input data type [%s]"
                    % (item_prefix, item_config[cf_input_data_type])
                )
                logger.error("%s : SKIPPED" % (item_prefix))
                continue

        if cf_output_path_create not in item_config:
            item_config[cf_output_path_create] = False

        if cf_output_file_mode in item_config:
            if not isinstance(item_config[cf_output_file_mode], str):
                item_config[cf_output_file_mode] = str(
                    item_config[cf_output_file_mode]
                )

        # add new item to work
        logger.info("%s : OK" % item_prefix)
        validated_items.append(item_config)

    #
    if not is_items_valid:
        logger.error("Can not continue with this config file")
        return []

    return validated_items


def doit(cfg):

    if len(cfg) == 0:
        logger.error("No valid data in config. Nothing to do")
        return False

    for item_index, item in enumerate(cfg):
        item_prefix = "exec [%s] (%s)" % (item_index, item[cf_name])
        logger.info(
            "%s : Started. Mode: %s Output path: %s"
            % (item_prefix, item[cf_mode], item[cf_output_path])
        )

        if not os.path.exists(item[cf_template]):
            logger.error(
                "%s : Template file not found: %s." % (item_prefix, item[cf_template])
            )
            continue

        try:
            with open(item[cf_template]) as fh:
                j2_template = jinja2.Template(fh.read())
        except jinja2.TemplateSyntaxError as err:
            logger.error(
                "%s : Template syntax error in file %s: %s"
                % (item_prefix, item[cf_template], err.message)
            )
            return False
        except IOError:
            logger.error(
                "%s : Error reading template file: %s"
                % (item_prefix, item[cf_template])
            )
            return False

        # Reading input data
        match item[cf_input_data_type]:

            case "yml":
                try:
                    with open(item[cf_input_data_file], "r") as fh:
                        content_data = yaml.safe_load(fh)
                except IOError:
                    logger.error(
                        "%s : Error in parsing YML file: %s"
                        % (item_prefix, item[cf_input_data_file])
                    )
                    return False

            case "txt":
                content_data = []
                try:
                    with open(item[cf_input_data_file], "r") as fh:
                        for line in fh:
                            li = line.strip()
                            if len(li) == 0:
                                continue
                            if not li.startswith("#"):
                                content_data.append(shlex.split(li))
                except IOError:
                    logger.error(
                        "%s : Error reading file: %s"
                        % (item_prefix, item[cf_input_data_file])
                    )
                    return False

                if len(content_data) == 0:
                    logger.error(
                        "%s : No data in file: %s"
                        % (item_prefix, item[cf_input_data_file])
                    )
                    return False

        # Debug
        logger.debug(f"content data: {content_data}")

        # by default additional data not present
        additional_data = {}
        additional_data_from_config = {}
        additional_data_from_file = {}

        #
        if cf_additional_data in item:
            additional_data_from_config = item[cf_additional_data]
            logger.debug(f"additional_data from config: {additional_data_from_config}")

        # if additional_data_file present in config
        if cf_additional_data_file in item:
            if os.path.exists(item[cf_additional_data_file]):
                # Reading additional data
                try:
                    logger.debug(
                        f'Reading additional data file"  {item[cf_additional_data_file]}'
                    )
                    with open(item[cf_additional_data_file], "r") as fh:
                        additional_data_from_file = yaml.safe_load(fh)
                    logger.debug(
                        f"additional_data from file: {additional_data_from_file}"
                    )
                except IOError:
                    logger.error(
                        "%s : Error reading additional data file: %s"
                        % (item_prefix, item[cf_additional_data_file])
                    )
                    return False

        # Merging additional data
        additional_data = {**additional_data_from_file, **additional_data_from_config}
        logger.debug(f"additional_data: {additional_data}")

        # Checking for existing OUTPUT directory
        try:
            result = os.path.isdir(item[cf_output_path])
            if not result:
                if item[cf_output_path_create]:
                    logger.info(
                        "%s : Creation directory: %s"
                        % (item_prefix, item[cf_output_path])
                    )
                    os.makedirs(item[cf_output_path], exist_ok=True)
                else:
                    logger.error(
                        "%s : Output directory not found: %s"
                        % (item_prefix, item[cf_output_path])
                    )
                    continue
        except IOError:
            logger.error(
                "%s : Output directory checking error: %s"
                % (item_prefix, item[cf_output_path])
            )
            return False

        # Working ...
        match item[cf_mode]:
            case "all":

                # generate path
                j2_template_output_path = jinja2.Template(item[cf_output_path])
                output_path = j2_template_output_path.render(
                    content=content_data, ad=additional_data
                )

                # generate file name
                j2_template_output_file = jinja2.Template(
                    item[cf_output_file_name_template]
                )
                output_file_name = j2_template_output_file.render(
                    content=content_data, ad=additional_data
                )
                output_file_name = os.path.join(output_path, output_file_name)

                # render, and save the results to file
                logger.info("%s : Output file: %s" % (item_prefix, output_file_name))

                try:
                    with open(output_file_name, "w") as fh:
                        fh.write(
                            j2_template.render(content=content_data, ad=additional_data)
                        )
                except jinja2.TemplateError as err:
                    logger.error(
                        "%s : Template error : %s" % (item_prefix, err.message)
                    )
                except IOError:
                    logger.error(
                        "%s : Writing file IOError : %s"
                        % (item_prefix, output_file_name)
                    )
                    continue

                # set file mode
                if cf_output_file_mode in item:
                    os.chmod(output_file_name, int(item[cf_output_file_mode], 8))

            case "one":

                logger.debug("Data type of content: %s" % type(content_data))

                for data_index, item_content in enumerate(content_data):

                    # generate path
                    j2_template_output_path = jinja2.Template(item[cf_output_path])
                    output_path = j2_template_output_path.render(
                        item=item_content, ad=additional_data
                    )

                    # generate file name
                    j2_template_output_file = jinja2.Template(
                        item[cf_output_file_name_template]
                    )
                    output_file_name = j2_template_output_file.render(
                        item=item_content, ad=additional_data
                    )
                    output_file_name = os.path.join(output_path, output_file_name)

                    # checking for existing files, it's no problem
                    if os.path.exists(output_file_name):
                        logger.info(
                            "%s : Overwriting output file: %s"
                            % (item_prefix, output_file_name)
                        )
                    else:
                        logger.info(
                            "%s : Output file: %s" % (item_prefix, output_file_name)
                        )

                    try:
                        with open(output_file_name, "w") as fh:
                            fh.write(
                                j2_template.render(
                                    content=item_content, ad=additional_data
                                )
                            )
                    except IOError:
                        logger.error(
                            "%s : Writing file IOError : %s"
                            % (item_prefix, output_file_name)
                        )
                        continue

                    # set file mode
                    if cf_output_file_mode in item:
                        os.chmod(
                            output_file_name, int(item[cf_output_file_mode], 8)
                        )

            case _:
                logging.error(f"Unknown mode value {item[cf_mode]}")

        # end of match
        logger.info("%s : Done" % item_prefix)
    return True


def main():

    args = parse_arguments()
    logger.info(f"Started {APP} {VERSION} {GITHUBURL}")

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info("Config file: %s" % args.config)

    cfg = check_config_file(args.config)
    # if only check config
    if args.check:
        sys.exit(0 if cfg else 1)

    if not cfg:
        sys.exit(1)

    #
    if not doit(cfg):
        sys.exit(1)
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

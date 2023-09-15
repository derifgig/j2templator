# J2Templator

Tool for generate files from Jinja2 templates.

Config file - YAML

Source data file format - YAML | TXT

# Config file example: `j2templator.yaml`

## Config item elements description

`name` - Title of config item

`template` - (required) path to template file (Jinja2)

`check_ingore_file_absent` - [yes,**no**] ignore error of absent file on checking

`input_data_file` - (required) source data

`input_data_type` - [**yml**|txt]

`additional_data_file` - [yml] some data array, be a part of each item

`output_path` - directory (required) for output data

`output_path_create` - [yes,**no**] should we create output directory

`output_file_name_template` - (required) output file name pattern. Cat use jinja2 syntax for items from data file

`mode` - [**all**|one] will be created one output file, 'one' - will be created separated file for each item of input data

## Install for current user 

Check for `~/.local/bin` is present in `PATH`.

```bash
mkdir ~/.local/bin -p
cp j2templator.py ~/.local/bin/j2templator
chmod +x ~/.local/bin/j2templator
```

## Install to system 

```bash
sudo cp j2templator.py /usr/local/bin/j2templator
sudo chmod +x /usr/local/bin/j2templator
```

## Run

```bash
# Example data in this project
python3 j2templator.py -c j2templator.yaml

# 
j2templator -c /path/to/file/config.yaml
```
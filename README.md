# J2Templator

Tool for generate files from Jinja2 templates.
Config file - YAML
Source data file format - YAML

## Config file 

```yaml
---
- name: "Example Item 1" 
  template: ./data/example00/template00.j2
  input_data_file_yaml: ./data/example00/data.yaml
  output_path: ./output/
  output_path_create: yes
  output_file_name_template: output-one-{{ }}.conf
  mode: one
```

### Config item elements description

`name` - Title of config item

`template` - (required) path to template file (Jinja2)

`input_data_file_yaml` - (required) source data in YAML format

`output_path` - directory (required) for output data

`output_path_create` - [yes,no(default)] should script create output directory

`output_file_name_template` - (required) output file name pattern. Cat use jinja2 syntax for items from data file

`mode` - [all|one] 'all'(default) -  will be created one output file, 'one' - will be created separated file for each item of input data

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
python3 j2templator.py --config data/config-example-00.yaml

# 
j2templator -c /path/to/file/config.yaml
```
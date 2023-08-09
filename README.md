# J2Templator

Tool for generate files from Jinja2 templates.
Config file - YAML
Source data file format - YAML

# Run
```bash
python3 j2templator.py --config data/config-example-00.yaml
```

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
### Elements description
'name' - Title of config item
'template' - (required) path to template file (Jinja2)
'input_data_file_yaml' - (required) source data in YAML format
'output_path' - directory (required) for output data
'output_path_create' - [yes,no(default)] should script create output directory
'output_file_name_template' - (required) output file name pattern. Cat use jinja2 syntax for items from data file. 
'mode' - possible values: 'all'(default) -  will be created one output file, 'one' - will be created separated file for each item of input data


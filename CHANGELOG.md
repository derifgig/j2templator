# CHANGE LOG

## Version 0.4  2023-11-30
- Fixed issue: values in quotes in source txt file

## Version 0.3 
 - Added exception "Template syntax error" for j2 templates
 - Added key "-k|--check" : only check configuration mode

## Version 0.2 - 2023-08-21
  - field `input_data_type_yml` replaced with `input_data_file` and `input_data_type`
  - `input_data_type`: [yml|txt]. TXT format one line - one item, space is delimiter 
  - prefix `work` in log replaced by `exec`
  - added additional data from `additional_data_file` as variable `ad` 
  - added option `check_ingore_file_absent`

## Version 0.1 
  - basic functional
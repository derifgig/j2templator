#!/bin/bash
#
python3 jtemplator.py --config data/config-example-00.yaml --verbose
#
echo -e '\n========= NO VERBOSE =============\n'
python3 jtemplator.py --config data/config-example-00.yaml

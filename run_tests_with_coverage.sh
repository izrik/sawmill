#!/bin/bash

coverage run --source=sawmill,models ./run_tests.py "$@"
coverage html

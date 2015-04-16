#!/bin/bash -e

source venv/bin/activate
make test
make zipfile

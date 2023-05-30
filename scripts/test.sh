#!/usr/bin/env bash
pip install -e .[dev] -qqq
coverage run -m pytest tests ${@}

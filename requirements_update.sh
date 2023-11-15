#!/usr/bin/env bash

poetry export -f requirements.txt --without-hashes --with dev > requirements_dev.txt
poetry export -f requirements.txt --without-hashes > requirements.txt

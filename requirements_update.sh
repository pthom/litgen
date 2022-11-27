#!/usr/bin/env bash

poetry export -f requirements.txt --without-hashes --dev > requirements.txt

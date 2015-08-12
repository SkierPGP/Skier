#!/usr/bin/env bash

gunicorn -c gunicorn_config.py app:app
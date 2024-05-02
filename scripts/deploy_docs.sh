#!/bin/bash

cd "$(dirname "$0")"

source ../.venv/Scripts/activate
python deploy_docs.py

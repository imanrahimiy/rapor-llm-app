#!/usr/bin/env bash

set -e

echo "Installing dependencies..."

pip install -r requirements.txt

echo "Running RAPOR-LLM reproducibility script..."

python reproduce.py

echo "Done."

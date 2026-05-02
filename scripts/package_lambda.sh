#!/usr/bin/env bash
set -euo pipefail

# Packages the FastAPI app for AWS Lambda.
# Run this from the repo root after installing dependencies in your local environment.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build/lambda"
ZIP_PATH="$ROOT_DIR/build/lambda-deploy.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

python3 -m pip install --upgrade pip
python3 -m pip install -r "$ROOT_DIR/requirements.txt" -t "$BUILD_DIR"

cp -R "$ROOT_DIR/app" "$BUILD_DIR/app"
cp "$ROOT_DIR/lambda_handler.py" "$BUILD_DIR/"
cp "$ROOT_DIR/.env.aws.example" "$BUILD_DIR/.env.example.aws"

(
  cd "$BUILD_DIR"
  zip -r "$ZIP_PATH" .
)

echo "Lambda package created at: $ZIP_PATH"

#!/usr/bin/env bash

python3 -m uvicorn src.app:create_app --factory --host 0.0.0.0
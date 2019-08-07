#!/bin/bash
git pull && python3 generate.py -o ./nginx && docker-compose up -d --force-recreate

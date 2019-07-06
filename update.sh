#!/bin/bash
git pull && python3 generate.py && docker-compose up -d --force-recreate

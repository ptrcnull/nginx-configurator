#!/bin/bash
git pull && python3 generate.js && docker-compose down && docker-compose up -d

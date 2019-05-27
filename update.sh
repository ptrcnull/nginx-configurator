#!/bin/bash
git pull && node generate.js && docker-compose down && docker-compose up -d

#!/bin/bash
exec gunicorn main:app --bind 0.0.0.0:5050 --access-logfile -
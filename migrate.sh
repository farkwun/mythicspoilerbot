#!/bin/bash
python create_tables.py
python migrate_tables.py
chown www-data db/test_table.db

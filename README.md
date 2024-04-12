# Flyway Schema History Restore
## This python script can generate a DDL script to insert the correct values (including checksum) into your flyway_schema_history table.

### Requirements 
[Install Python3](https://www.python.org/downloads/)

### Usage
Navigate to the script directory and execute the following command in your terminal
```bash
python3 flyway_history_restore.py
```

Enter the path to your db.migrations folder:
```bash
db.migrations path: your-path/your-project/src/main/resources/db/migration
```

Choose the database dialect for the DDL:
```bash
###### AVAILABLE DATABASES  ######

1 - POSTGRESQL
2 - ORACLE

select: 1
```

The file will be generated in the same directory as the Python script:
```bash
flyway_history_restore_POSTGRESQL_2024-04-12-15-43-05.sql
```

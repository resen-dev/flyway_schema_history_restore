import os
import re
import zlib
from datetime import datetime
from enum import Enum


class DB(Enum):
    POSTGRESQL = "1"
    ORACLE = "2"


def calculate_crc32(filepath):
    crc32 = zlib.crc32(b'')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            trimmed_line = line.strip('\r\n')
            crc32 = zlib.crc32(trimmed_line.encode('utf-8'), crc32)

    if crc32 > 0x7FFFFFFF:
        crc32 -= 0x100000000

    return crc32


def extract_number(filename):
    match = re.search(r'V(\d+)', filename)
    return int(match.group(1)) if match else None


def set_path():

    path = input('db.migrations path: ')

    while input(f'\nis the path { os.path.abspath(path)} \ncorrect? [y/n]: ') not in ['Y', 'y']:
        path = input('correct db.migrations path: ')

    return path


def set_db():
    print("\n###### AVAILABLE DATABASES  ######\n")

    for db in DB:
        print(db.value, "-", db.name)

    set_db = input("\nselect: ")

    while set_db not in [db.value for db in DB]:
        set_db = input("select valid db (or n to exit): ")
        if set_db in ['N', 'n']:
            exit()

    return set_db


def get_ddl_insert_header(db):

    if db == DB.POSTGRESQL.value:
        return """
            INSERT INTO flyway_schema_history (
                installed_rank,
                version,
                description,
                type,
                script,
                checksum,
                installed_by,
                installed_on,
                execution_time,
                success
            ) VALUES
        """

    if db == DB.ORACLE.value:
        return """
INSERT INTO flyway_schema_history (
    installed_rank,
    version,
    description,
    type,
    script,
    checksum,
    installed_by,
    installed_on,
    execution_time,
    success
) VALUES
        """


def get_ddl_insert_value(db, file, filename, last, index):

    version = filename.replace("V__", "").split("_")[0].replace("V", "")
    script_name = filename.replace(".sql", "").replace(f"V{version}__", "").replace("_", " ")
    crc32 = calculate_crc32(file)
    exec_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    if db == DB.POSTGRESQL.value:
        return f"""
    (
        (
            SELECT COALESCE(MAX(installed_rank), 0) + {index + 1} FROM flyway_schema_history
        ),
        '{version}',
        '{script_name}',
        'SQL',
        '{filename}',
        {crc32},
        'FLYWAY_HISTORY_RESTORE',
        '{exec_time}',
        0,
        true
    {");" if last else "),"}
        """

    if db == DB.ORACLE.value:
        return f"""
    (
        (
            SELECT COALESCE(MAX(installed_rank), 0) + {index + 1} FROM flyway_schema_history
        ),
        '{version}',
        '{script_name}',
        'SQL',
        '{filename}',
        {crc32},
        'FLYWAY_HISTORY_RESTORE',
        TO_TIMESTAMP('{exec_time}', 'YYYY-MM-DD HH24:MI:SS'),
        0,
        1
    {");" if last else "),"}
        """


if __name__ == "__main__":

    print("##### FLYWAY HISTORY RESTORE #####\n")

    migrations_path = set_path()

    files = sorted(os.listdir(migrations_path), key=extract_number)

    selected_db = set_db()

    script_ddl_insert_header = get_ddl_insert_header(selected_db)
    script_ddl_insert_values = []

    for index, file in enumerate(files):

        migrations_path_with_file = os.path.join(migrations_path, file)

        script_ddl_insert_values.append(
            get_ddl_insert_value(selected_db, migrations_path_with_file, file, file == files[-1], index)
        )

    with open(f"flyway_history_restore_{DB(selected_db).name}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.sql", 'w') as file:
        file.write(str(script_ddl_insert_header) + '\n')
        for ddl_insert_value in script_ddl_insert_values:
            file.write(str(ddl_insert_value) + '\n')

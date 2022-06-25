
name = "log2sql"

version = "0.0.1"

description = \
    """
    A backend for storing logging events to different `SQL` databases.
    """

uuid = "log2sqlite"

build_command = 'python {root}/build.py {install}'

variants = [
    ["platform-linux", "arch-x86_64", "os-Ubuntu-20+"]
]

def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.append("{root}/python")
    env.LOG2SQLITE_DB_USERNAME = "log2sqlite_admin"
    env.LOG2SQLITE_DB_PASSWORD = "password"
    env.LOG2SQLITE_DB_HOSTNAME = "localhost"
    env.LOG2SQLITE_DB_PORT = 3000
    env.LOG2SQLITE_DB_NAME = "log2sqlite_db"
    env.LOG2SQLITE_DB_DATA_DIR = "{root}/config"
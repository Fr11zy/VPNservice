from database.db import Database
import logging
import yaml
import argparse
import os

class FileNotExists(Exception):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = "VPN service")
    parser.add_argument('-db', '--database', type=str, help="path to database", default="db.sqlite", required=False)
    parser.add_argument('-s', '--schema', type=str, help="path to schema", default="config.yaml", required=False)
    parser.add_argument('-l', '--logname', type=str, help="path to logger", default="app.log", required=False)
    args = parser.parse_args()
    logger = logging.getLogger(args.logname)
    
    if not os.path.exists(args.schema) or not os.path.isfile(args.schema):
        raise FileNotExists(f"Schema file not found: {args.schema}")
    
    with open(args.schema, 'r') as f:
        schema = yaml.safe_load(f)
    
    db = Database(args.database)
    db.create_database(schema)
# base_sql.py
import os
from sqlalchemy import create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import lib.logger as logger
from lib.db.models import BASE


class Client(object):
    def __init__(self, db_name, host, user_name, password):
        self.db_name = db_name
        self.host = host
        self.user_name = user_name
        self.password = password
        self.url = URL.create(
            drivername="postgresql",
            username=self.user_name,
            host=self.host,
            database=self.db_name,
            password=self.password)
        self.engine = None
        self.session = None

    def connect(self):
        logger.DEBUG(f"Attempting connection {self.url}")
        self.engine = create_engine(self.url)
        self.engine.connect()
        logger.DEBUG("Connection successful")
        self.session = Session(self.engine)
        logger.DEBUG("Session Established")

    def create_all_tables(self):
        with self.session:
            try:
                # Generate schema
                BASE.metadata.create_all(self.engine)
                self.session.commit()
                logger.DEBUG(f"connected & db populated")
            except Exception as e:
                self.session.rollback()
                logger.ERROR(e)
                raise e
        
    def insert(self, table, objects, ignore_duplicates=False):
        with self.session:
            try:
                self.session.bulk_insert_mappings(table, objects)
                self.session.commit()
                logger.DEBUG(f"Added objects")
            except Exception as e:
                if isinstance(e, IntegrityError) and ignore_duplicates:
                    logger.DEBUG("Ignoring Duplicate inserts exception"
                                 " as ignore_duplicates=True")
                else:
                    self.session.rollback()
                    logger.ERROR(e)
                    raise e

    def update(self, table, objects):
        with self.session:
            try:
                self.session.bulk_update_mappings(table, objects)
                self.session.commit()
                logger.DEBUG(f"Updated objects")
            except Exception as e:
                self.session.rollback()
                logger.ERROR(e)
                raise e

    def get_all(self, table, columns=None):
        result = []
        if columns:
            col_list = list(map(lambda name: getattr(table, name), columns))
            output = self.session.query(*col_list).all()
            for entry in output:
                result.append(dict(zip(col_list, entry)))
        else:
            output = self.session.query(table).all()
            for entry in output:
                result.append(vars(entry))
        return result


        

        
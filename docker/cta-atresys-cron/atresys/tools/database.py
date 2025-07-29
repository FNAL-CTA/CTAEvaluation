import os
import atexit

from sqlalchemy import create_engine
from tools.models import ScannedForRepack, RepackStatusProd
from yaml import safe_load
from datetime import datetime


class Database:
    def __init__(self, config_file=None):
        try:
            cfg = safe_load(open(config_file, 'r'))
            db_config = cfg["tools"]["cta-ops-repack-automation"]['database']
            db_url = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{int(db_config['port'])}/{db_config['name']}"
            self.engine = create_engine(db_url)
            self.connection = self.engine.connect()
            atexit.register(self.close)
        except Exception as e:
            raise ValueError(f"Failed to load database configuration: {e}")

    def close(self):
        self.connection.close()

    def add_scanned_objects(self, results):
        if len(results.get('output', [])) > 0:
            timestamp = datetime.now().timestamp()
            vids = results['output']
            
            # check if the entries already exist
            existing_entries = {
                entry.vid: entry 
                for entry 
                in self.connection.execute(
                    ScannedForRepack.__table__.select().where(ScannedForRepack.vid.in_(vids))
                ).fetchall()
            }
            self.connection.execute(
                ScannedForRepack.__table__.update()
                .where(ScannedForRepack.vid.in_(vids))
                .values(updated=timestamp)
            )
            for vid in vids:
                if vid not in existing_entries:
                    new_entry = ScannedForRepack(vid=vid, created=timestamp, updated=timestamp, status='Marked for review')
                    self.connection.execute(ScannedForRepack.__table__.insert(), new_entry.__dict__)
            
            self.connection.commit()
            self.clean_scanned_objects()
            
    def clean_scanned_objects(self):
        """
        Clean the scanned objects from the database.
        """
        self.connection.execute(
            ScannedForRepack.__table__.delete().where(
                ScannedForRepack.vid.in_(
                    RepackStatusProd.__table__.select().with_only_columns(RepackStatusProd.__table__.c.tape)
                )
            )
        )
        self.connection.commit()

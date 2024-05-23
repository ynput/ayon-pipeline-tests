"""
    Helper class for automatic testing, provides restore via server endpoint.

"""
import os

import time

import ayon_api

DUMP_FILE_FORMAT = "dump.{project_name}.sql"
PROJECT_IMPORT_TIMEOUT = 30  # in seconds


class DBHandler:

    def setup_empty(self, name):
        # not much sense
        self.db = self.client[name]

    def setup_from_dump(self,
        db_name, dump_dir, overwrite=False, db_name_out=None):
        """
            Restores 'db_name' from 'dump_dir'.

            Args:
                db_name (str): source DB name
                dump_dir (str): folder with dumped subfolders
                overwrite (bool): True if overwrite target
                db_name_out (str): name of target DB, if empty restores to
                    source 'db_name'
        """
        db_name_out = db_name_out or db_name

        if self._db_exists(db_name_out):
            if not overwrite:
                raise RuntimeError("DB {} already exists".format(db_name_out) +
                                   "Run with overwrite=True")
            else:
                self.teardown(db_name_out)

        sql_path = os.path.join(dump_dir,
                                DUMP_FILE_FORMAT.format(project_name=db_name))
        con = ayon_api.get_server_api_connection()
        response = con.upload_file(
            "addons/projectimport/1.0.1/upload",  # TODO query actual version
            sql_path,
            request_type=ayon_api.server_api.RequestTypes.post
        )
        self._wait_for_import(response)

    def teardown(self, db_name):
        """Drops 'db_name' if exists."""
        if not self._db_exists(db_name):
            print("{} doesn't exist".format(db_name))
            return

        print("Dropping {} database".format(db_name))
        con = ayon_api.get_server_api_connection()
        con.delete_project(db_name)

    def _db_exists(self, db_name):
        return ayon_api.get_project(db_name)

    def _wait_for_import(self, response):
        """Waits for event to be finished

        Throws:
            RuntimeError
        """
        try:
            event_id = response.json()["eventId"]
        except KeyError:
            raise RuntimeError("Dump upload failed.")
        status = "in_progress"
        sleep_step = 0.2
        elapsed = 0
        while status == "in_progress":
            event = ayon_api.get_event(event_id)
            status = event["status"]
            elapsed += sleep_step
            if elapsed > PROJECT_IMPORT_TIMEOUT:
                break
            time.sleep(sleep_step)
        if event["status"] != "finished":
            raise RuntimeError(f"Import of database failed for {event_id}")

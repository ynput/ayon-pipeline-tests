"""Testing classes for module testing and publishing in hosts."""
import os
import sys
import six
import json
import pytest
import tempfile
import shutil
import glob

from tests.lib.db_handler import DBHandler
from tests.lib.file_handler import RemoteFileHandler


class BaseTest:
    """Empty base test class"""


class ModuleUnitTest(BaseTest):
    """Generic test class for testing modules

        Use PERSIST==True to keep temporary folder and DB prepared for
        debugging or preparation of test files.

        Implemented fixtures:
            monkeypatch_session - fixture for env vars with session scope
            download_test_data - tmp folder with extracted data from GDrive
            env_var - sets env vars from input file
            db_setup - prepares avalon AND openpype DBs for testing from
                        binary dumps from input data
            dbcon - returns DBConnection to AvalonDB
            dbcon_openpype - returns DBConnection for OpenpypeMongoDB

    """
    PERSIST = False  # True to not purge temporary folder nor test DB

    TEST_OPENPYPE_MONGO = "mongodb://localhost:27017"
    TEST_DB_NAME = "test_db"
    TEST_PROJECT_NAME = "test_project"
    TEST_OPENPYPE_NAME = "test_openpype"

    TEST_FILES = []

    PROJECT = "test_project"
    ASSET = "test_asset"
    TASK = "test_task"

    @pytest.fixture(scope='session')
    def monkeypatch_session(self):
        """Monkeypatch couldn't be used with module or session fixtures."""
        from _pytest.monkeypatch import MonkeyPatch
        m = MonkeyPatch()
        yield m
        m.undo()

    @pytest.fixture(scope="module")
    def download_test_data(self):
        tmpdir = tempfile.mkdtemp()
        for test_file in self.TEST_FILES:
            file_id, file_name, md5 = test_file

            f_name, ext = os.path.splitext(file_name)

            RemoteFileHandler.download_file_from_google_drive(file_id,
                                                              str(tmpdir),
                                                              file_name)

            if ext.lstrip('.') in RemoteFileHandler.IMPLEMENTED_ZIP_FORMATS:
                RemoteFileHandler.unzip(os.path.join(tmpdir, file_name))
            print("Temporary folder created:: {}".format(tmpdir))
            yield tmpdir

            if not self.PERSIST:
                print("Removing {}".format(tmpdir))
                shutil.rmtree(tmpdir)

    @pytest.fixture(scope="module")
    def env_var(self, monkeypatch_session, download_test_data):
        """Sets temporary env vars from json file."""
        env_url = os.path.join(download_test_data, "input",
                               "env_vars", "env_var.json")
        if not os.path.exists(env_url):
            raise ValueError("Env variable file {} doesn't exist".
                             format(env_url))

        env_dict = {}
        try:
            with open(env_url) as json_file:
                env_dict = json.load(json_file)
        except ValueError:
            print("{} doesn't contain valid JSON")
            six.reraise(*sys.exc_info())

        for key, value in env_dict.items():
            all_vars = globals()
            all_vars.update(vars(ModuleUnitTest))  # TODO check
            value = value.format(**all_vars)
            print("Setting {}:{}".format(key, value))
            monkeypatch_session.setenv(key, str(value))
        import openpype

        openpype_root = os.path.dirname(os.path.dirname(openpype.__file__))
        # ?? why 2 of those
        monkeypatch_session.setenv("OPENPYPE_ROOT", openpype_root)
        monkeypatch_session.setenv("OPENPYPE_REPOS_ROOT", openpype_root)

    @pytest.fixture(scope="module")
    def db_setup(self, download_test_data, env_var, monkeypatch_session):
        """Restore prepared MongoDB dumps into selected DB."""
        backup_dir = os.path.join(download_test_data, "input", "dumps")

        uri = os.environ.get("OPENPYPE_MONGO")
        db_handler = DBHandler(uri)
        db_handler.setup_from_dump(self.TEST_DB_NAME, backup_dir, True,
                                   db_name_out=self.TEST_DB_NAME)

        db_handler.setup_from_dump("openpype", backup_dir, True,
                                   db_name_out=self.TEST_OPENPYPE_NAME)

        yield db_handler

        if not self.PERSIST:
            db_handler.teardown(self.TEST_DB_NAME)
            db_handler.teardown(self.TEST_OPENPYPE_NAME)

    @pytest.fixture(scope="module")
    def dbcon(self, db_setup):
        """Provide test database connection.

            Database prepared from dumps with 'db_setup' fixture.
        """
        from avalon.api import AvalonMongoDB
        dbcon = AvalonMongoDB()
        dbcon.Session["AVALON_PROJECT"] = self.TEST_PROJECT_NAME
        yield dbcon

    @pytest.fixture(scope="module")
    def dbcon_openpype(self, db_setup):
        """Provide test database connection for OP settings.

            Database prepared from dumps with 'db_setup' fixture.
        """
        from openpype.lib import OpenPypeMongoConnection
        mongo_client = OpenPypeMongoConnection.get_mongo_client()
        yield mongo_client[self.TEST_OPENPYPE_NAME]["settings"]


class PublishTest(ModuleUnitTest):
    """Test class for publishing in hosts.

        Implemented fixtures:
            launched_app - launches APP with last_workfile_path
            publish_finished - waits until publish is finished, host must
                kill its process when finished publishing. Includes timeout
                which raises ValueError

        Not implemented:
            last_workfile_path - returns path to testing workfile
            startup_scripts - provide script for setup in host

        Implemented tests:
            test_folder_structure_same - compares published and expected
                subfolders if they contain same files. Compares only on file
                presence

            TODO: implement test on file size, file content
    """

    APP = ""
    APP_VARIANT = ""

    APP_NAME = "{}/{}".format(APP, APP_VARIANT)

    TIMEOUT = 120  # publish timeout

    @pytest.fixture(scope="module")
    def last_workfile_path(self, download_test_data):
        raise NotImplementedError

    @pytest.fixture(scope="module")
    def startup_scripts(self, monkeypatch_session, download_test_data):
        raise NotImplementedError

    @pytest.fixture(scope="module")
    def launched_app(self, dbcon, download_test_data, last_workfile_path,
                     startup_scripts):
        """Launch host app"""
        # set publishing folders
        root_key = "config.roots.work.{}".format("windows")  # TEMP
        dbcon.update_one(
            {"type": "project"},
            {"$set":
                {
                    root_key: download_test_data
                }}
        )

        # set schema - for integrate_new
        from openpype import PACKAGE_DIR
        # Path to OpenPype's schema
        schema_path = os.path.join(
            os.path.dirname(PACKAGE_DIR),
            "schema"
        )
        os.environ["AVALON_SCHEMA"] = schema_path

        import openpype
        openpype.install()
        os.environ["OPENPYPE_EXECUTABLE"] = sys.executable
        from openpype.lib import ApplicationManager

        application_manager = ApplicationManager()
        data = {
            "last_workfile_path": last_workfile_path,
            "start_last_workfile": True,
            "project_name": self.PROJECT,
            "asset_name": self.ASSET,
            "task_name": self.TASK
        }

        yield application_manager.launch(self.APP_NAME, **data)

    @pytest.fixture(scope="module")
    def publish_finished(self, dbcon, launched_app, download_test_data):
        """Dummy fixture waiting for publish to finish"""
        import time
        time_start = time.time()
        while launched_app.poll() is None:
            time.sleep(0.5)
            if time.time() - time_start > self.TIMEOUT:
                raise ValueError("Timeout reached")

        # some clean exit test possible?
        print("Publish finished")
        yield True

    def test_folder_structure_same(self, dbcon, publish_finished,
                                   download_test_data):
        """Check if expected and published subfolders contain same files.

            Compares only presence, not size nor content!
        """
        published_dir_base = download_test_data
        published_dir = os.path.join(published_dir_base,
                                     self.PROJECT,
                                     self.TASK,
                                     "**")
        expected_dir_base = os.path.join(published_dir_base,
                                         "expected")
        expected_dir = os.path.join(expected_dir_base,
                                    self.PROJECT,
                                    self.TASK,
                                    "**")

        published = set(f.replace(published_dir_base, '') for f in
                        glob.glob(published_dir, recursive=True) if
                        f != published_dir_base and os.path.exists(f))
        expected = set(f.replace(expected_dir_base, '') for f in
                       glob.glob(expected_dir, recursive=True) if
                       f != expected_dir_base and os.path.exists(f))

        not_matched = expected.difference(published)
        assert not not_matched, "Missing {} files".format(not_matched)

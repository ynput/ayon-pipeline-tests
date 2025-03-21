"""Testing classes for module testing and publishing in hosts."""
import os
import sys
import six
import json
import pytest
import tempfile
import shutil
import glob
import platform
import requests
import re
import inspect
import time
import logging

import ayon_api

from ayon_core.addon import AddonsManager
from ayon_core.settings import get_project_settings
from ayon_api import (
    get_server_api_connection,
    get_folder_by_path,
    get_task_by_name,
    get_project,
)
from ayon_core.pipeline import Anatomy

from ayon_pipeline_tests.tests.lib.db_handler import DBHandler
from ayon_pipeline_tests.tests.lib.file_handler import (
    RemoteFileHandler,
    LocalFileHandler
)


class BaseTest:
    """Empty base test class"""


class ModuleUnitTest(BaseTest):
    """Generic test class for testing modules

    Use PERSIST==True to keep temporary folder and DB prepared for
    debugging or preparation of test files.

    Implemented fixtures:
        monkeypatch_session - fixture for env vars with session scope
        project_settings - fixture for project settings with session scope
        download_test_data - tmp folder with extracted data from GDrive
        env_var - sets env vars from input file
        db_setup - prepares DB for testing from sql dumps from input data

    """
    PERSIST = False  # True to not purge temporary folder nor test DB

    TEST_FILES = []

    PROJECT = "test_project"
    FOLDER_PATH = "/test_asset"
    TASK = "test_task"

    TEST_DB_NAME = "test_project"

    TEST_DATA_FOLDER = None

    @property
    def log(self):
        """Dynamic logger based on the class name."""
        return logging.getLogger(self.__class__.__name__)

    @pytest.fixture(scope='session')
    def monkeypatch_session(self):
        """Monkeypatch couldn't be used with module or session fixtures."""
        from _pytest.monkeypatch import MonkeyPatch
        m = MonkeyPatch()
        yield m
        m.undo()

    @pytest.fixture(scope='module')
    def project_settings(self):
        yield get_project_settings(
            self.PROJECT
        )

    @pytest.fixture(scope="module")
    def download_test_data(
        self, test_data_folder, persist, request, dump_databases
    ):
        test_data_folder = test_data_folder or self.TEST_DATA_FOLDER
        if test_data_folder:
            print("Using existing folder {}".format(test_data_folder))
            yield test_data_folder
        else:
            tmpdir = tempfile.mkdtemp()
            print("Temporary folder created:: {}".format(tmpdir))
            for test_file in self.TEST_FILES:
                file_id, file_name, md5 = test_file

                current_dir = os.path.dirname(os.path.abspath(
                    inspect.getfile(self.__class__)))
                if os.path.exists(file_id):
                    handler_class = LocalFileHandler
                elif os.path.exists(os.path.join(current_dir, file_id)):
                    file_id = os.path.join(current_dir, file_id)
                    handler_class = LocalFileHandler
                else:
                    handler_class = RemoteFileHandler

                handler_class.download_test_source_files(file_id, str(tmpdir),
                                                         file_name)
                ext = None
                if "." in file_name:
                    _, ext = os.path.splitext(file_name)

                if ext and ext.lstrip('.') in handler_class.IMPLEMENTED_ZIP_FORMATS:  # noqa: E501
                    handler_class.unzip(os.path.join(tmpdir, file_name))

            yield tmpdir

            persist = (persist or self.PERSIST or
                       self.is_test_failed(request) or dump_databases)
            print(f"persist::{persist}, testfailed::{self.is_test_failed(request)}")
            with open("c:/projects/test.txt", "w") as fp:
                fp.write(f"persist::{persist}, testfailed::{self.is_test_failed(request)}")
            if not persist:
                print("Removing {}".format(tmpdir))
                shutil.rmtree(tmpdir)

    @pytest.fixture(scope="module")
    def output_folder_url(self, download_test_data):
        """Returns location of published data, cleans it first if exists."""
        path = os.path.join(download_test_data, "output")
        if os.path.exists(path):
            print("Purging {}".format(path))
            shutil.rmtree(path)
        yield path

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

        # TODO remove when test files will be cleaned up
        obsolete_env_vars = set(["OPENPYPE_MONGO",
                                 "AVALON_MONGO",
                                 "AVALON_DB",
                                 "OPENPYPE_DATABASE_NAME",
                                 "AVALON_PROJECT",
                                 "PYPE_DEBUG",
                                 "AVALON_CONFIG"])
        for key, value in env_dict.items():
            if key in obsolete_env_vars:
                continue
            all_vars = globals()
            all_vars.update(vars(ModuleUnitTest))  # TODO check
            value = value.format(**all_vars)
            print("Setting {}:{}".format(key, value))
            monkeypatch_session.setenv(key, str(value))

        import ayon_core
        ayon_core_root = os.path.dirname(os.path.dirname(ayon_core.__file__))

        monkeypatch_session.setenv("AYON_CORE_ROOT", ayon_core_root)

        # for remapping purposes (currently in Nuke)
        monkeypatch_session.setenv("TEST_SOURCE_FOLDER", download_test_data)

    @pytest.fixture(scope="module")
    def db_setup(
            self,
            download_test_data,
            env_var,
            monkeypatch_session,
            request,
            dump_databases,
            persist
    ):
        """Restore prepared Postgre dumps into selected DB."""
        backup_dir = os.path.join(download_test_data, "input", "dumps")
        db_handler = DBHandler()
        db_handler.setup_from_dump(self.TEST_DB_NAME, backup_dir,
                                   overwrite=True,
                                   db_name_out=self.TEST_DB_NAME)

        self._update_anatomy_roots(download_test_data)

        self.update_addon_versions()
        yield db_handler

        if dump_databases:
            print("Dumping databases to {}".format(download_test_data))
            output_dir = os.path.join(download_test_data, "output", "dumps")
            db_handler.backup_to_dump(
                self.TEST_DB_NAME, output_dir, format=dump_databases
            )

        # TODO temporarily, projectimport doesn't handle non existent project
        # persist = persist or self.PERSIST or self.is_test_failed(request)
        # if not persist:
        #     db_handler.teardown(self.TEST_DB_NAME)

    def update_addon_versions(self):
        """Implement changes of current addon version from dumped version.

        It is expected that testing class will override this method, where
        it will provide values for project_name,addon_name, addon_db_version
        and call _update_addon_versions
        """
        pass
        #self._update_addon_versions(project_name, addon_name, old_version)

    def _update_addon_versions(
            self, project_name,addon_name, addon_db_version):
        """Implement changes of current addon version from dumped version."""
        bundles = ayon_api.get_bundles()
        production_bundle = None
        for bundle in bundles["bundles"]:
            if bundle["name"] == bundles["productionBundle"]:
                production_bundle = bundle
                break

        current_version = production_bundle["addons"].get(addon_name)

        if not current_version:
            raise RuntimeError(f"{addon_name} not set in production bundle")

        endpoint = f"addons/{addon_name}/{addon_db_version}/rawOverrides/{project_name}"  # noqa
        response = ayon_api.get(endpoint)
        response.raise_for_status()
        raw_addon_settings = response.data

        if raw_addon_settings:
            self.log.debug(f"Creating new settings for {current_version}")
            endpoint = f"addons/{addon_name}/{current_version}/rawOverrides/{project_name}"
            response = ayon_api.put(endpoint, **raw_addon_settings)
            response.raise_for_status()

    def is_test_failed(self, request):
        return getattr(request.node, "module_test_failure", False)

    def _update_anatomy_roots(self, download_test_data):
        con = get_server_api_connection()
        project = con.get_project(self.PROJECT)
        platform_str = platform.system().lower()
        config = project["config"]
        output_dir = os.path.join(download_test_data, "output")
        for root_info in config["roots"].values():
            root_info[platform_str] = output_dir
        con.update_project(self.PROJECT, config=config)


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

    APP_GROUP = ""

    TIMEOUT = 120  # publish timeout

    # could be overwritten by command line arguments
    # command line value takes precedence

    # keep empty to locate latest installed variant or explicit
    APP_VARIANT = ""
    PERSIST = True  # True - keep test DB, outputted test files
    TEST_DATA_FOLDER = None  # use specific folder of unzipped test file

    SETUP_ONLY = False

    @pytest.fixture(scope="module")
    def app_name(self, app_variant, app_group):
        """Returns calculated value for ApplicationManager. Eg.(nuke/12-2)"""
        from ayon_applications import ApplicationManager
        app_variant = app_variant or self.APP_VARIANT
        app_group = app_group or self.APP_GROUP

        application_manager = ApplicationManager()
        if not app_variant:
            variant = (
                application_manager.find_latest_available_variant_for_group(
                    app_group
                )
            )
            app_variant = variant.name

        yield "{}/{}".format(app_group, app_variant)

    @pytest.fixture(scope="module")
    def app_args(self, download_test_data):
        """Returns additional application arguments from a test file.

            Test zip file should contain file at:
                FOLDER_DIR/input/app_args/app_args.json
            containing a list of command line arguments (like '-x' etc.)
        """
        app_args = []
        args_url = os.path.join(download_test_data, "input",
                                "app_args", "app_args.json")
        if not os.path.exists(args_url):
            print("App argument file {} doesn't exist".format(args_url))
        else:
            try:
                with open(args_url) as json_file:
                    app_args = json.load(json_file)

                if not isinstance(app_args, list):
                    raise ValueError
            except ValueError:
                print("{} doesn't contain valid JSON".format(args_url))
                six.reraise(*sys.exc_info())

        yield app_args

    @pytest.fixture(scope="module")
    def launched_app(
        self,
        startup_scripts,  # must stay here to load launch scripts
        db_setup,
        download_test_data,
        last_workfile_path,
        app_args, app_name,
        output_folder_url,
        setup_only
    ):
        """Launch host app"""
        if setup_only or self.SETUP_ONLY:
            print("Creating only setup for test, not launching app")
            yield
            return

        os.environ["AYON_EXECUTABLE"] = sys.executable
        from ayon_applications import ApplicationManager

        project_name = self.PROJECT
        project_entity = get_project(project_name)
        folder_entity = get_folder_by_path(
            project_name, self.FOLDER_PATH
        )
        task_entity = get_task_by_name(
            project_name, folder_entity["id"], self.TASK
        )
        anatomy = Anatomy(project_name)

        application_manager = ApplicationManager()
        data = {
            "last_workfile_path": last_workfile_path,
            "start_last_workfile": True,
            "project_name": self.PROJECT,
            "anatomy": anatomy,
            "project_entity": project_entity,
            "folder_path": self.FOLDER_PATH,
            "folder_entity": folder_entity,
            "task_entity": task_entity,
            "task_name": task_entity["name"],
        }
        if app_args:
            data["app_args"] = app_args

        app_process = application_manager.launch(app_name, **data)
        yield app_process

    @pytest.fixture(scope="module")
    def publish_finished(
        self,
        launched_app,
        download_test_data,
        timeout,
        setup_only
    ):
        """Dummy fixture waiting for publish to finish"""
        print(f"setup::{setup_only} - {self.SETUP_ONLY}")
        if setup_only or self.SETUP_ONLY:
            print("Creating only setup for test, not launching app")
            yield False
            return

        time_start = time.time()
        timeout = timeout or self.TIMEOUT
        timeout = float(timeout)
        while launched_app.poll() is None:
            time.sleep(0.5)
            if time.time() - time_start > timeout:
                launched_app.terminate()
                self.log.warning("Timeout '{timeout}' reached.")
                yield False

        # some clean exit test possible?
        print("Publish finished")
        yield True

    def test_folder_structure_same(
        self,
        publish_finished,
        download_test_data,
        output_folder_url,
        skip_compare_folders,
        setup_only
    ):
        """Check if expected and published subfolders contain same files.

        Compares only presence, not size nor content!
        """
        if setup_only or self.SETUP_ONLY:
            print("Creating only setup for test, not launching app")
            return

        published_dir_base = output_folder_url
        expected_dir_base = os.path.join(download_test_data,
                                         "expected")

        print(
            "Comparing published: '{}' | expected: '{}'".format(
                published_dir_base, expected_dir_base
            )
        )

        def get_files(dir_base):
            result = set()

            for f in glob.glob(dir_base + "\\**", recursive=True):
                if os.path.isdir(f):
                    continue

                if f != dir_base and os.path.exists(f):
                    result.add(f.replace(dir_base, ""))

            return result

        published = get_files(published_dir_base)
        expected = get_files(expected_dir_base)

        filtered_published = self._filter_files(
            published, skip_compare_folders
        )

        # filter out temp files also in expected
        # could be polluted by accident by copying 'output' to zip file
        filtered_expected = self._filter_files(expected, skip_compare_folders)

        not_matched = filtered_expected.symmetric_difference(
            filtered_published
        )
        if not_matched:
            raise AssertionError(
                "Missing {} files".format("\n".join(sorted(not_matched)))
            )

    def _filter_files(self, source_files, skip_compare_folders):
        """Filter list of files according to regex pattern."""
        filtered = set()
        for file_path in source_files:
            if skip_compare_folders:
                if not any([re.search(val, file_path)
                            for val in skip_compare_folders]):
                    filtered.add(file_path)
            else:
                filtered.add(file_path)

        return filtered


class DeadlinePublishTest(PublishTest):
    @pytest.fixture(scope="module")
    def publish_finished(
            self,
            launched_app,
            download_test_data,
            timeout,
            setup_only
    ):
        """Dummy fixture waiting for publish to finish"""
        if setup_only or self.SETUP_ONLY:
            print("Created only setup for test, app not launched")
            yield False
            return

        import time
        time_start = time.time()
        timeout = timeout or self.TIMEOUT
        timeout = float(timeout)
        while launched_app.poll() is None:
            time.sleep(0.5)
            if time.time() - time_start > timeout:
                launched_app.terminate()
                self.log.warning(f"Timeout '{timeout}' reached.")
                yield False
                return

        metadata_json = glob.glob(os.path.join(download_test_data,
                                               "output",
                                               "**/*_metadata.json"),
                                  recursive=True)
        if not metadata_json:
            self.log.warning(f"No DL metadata json found. "
                             "Publish failed before submission.")
            yield False
            return

        if len(metadata_json) > 1:
            # depends on creation order of published jobs
            metadata_json.sort(key=os.path.getmtime, reverse=True)

        with open(metadata_json[0]) as fp:
            job_info = json.load(fp)

        deadline_job_id = job_info["deadline_publish_job_id"]

        manager = AddonsManager()
        deadline_module = manager.addons_by_name["deadline"]
        deadline_url = (deadline_module.deadline_servers_info["default"]
                                                             ["value"])

        if not deadline_url:
            raise ValueError("Must have default deadline url.")

        url = "{}/api/jobs?JobId={}".format(deadline_url, deadline_job_id)
        valid_date_finished = None

        time_start = time.time()
        while not valid_date_finished:
            time.sleep(0.5)
            if time.time() - time_start > timeout:
                raise ValueError("Timeout for Deadline finish reached")

            response = requests.get(url, timeout=10)
            if not response.ok:
                msg = "Couldn't connect to {}".format(deadline_url)
                raise RuntimeError(msg)

            if not response.json():
                raise ValueError("Couldn't find {}".format(deadline_job_id))

            job = response.json()[0]

            def recursive_dependencies(job, results=None):
                if results is None:
                    results = []

                for dependency in job["Props"]["Dep"]:
                    dependency = requests.get(
                        "{}/api/jobs?JobId={}".format(
                            deadline_url, dependency["JobID"]
                        ),
                        timeout=10
                    ).json()[0]
                    results.append(dependency)
                    grand_dependencies = recursive_dependencies(
                        dependency, results=results
                    )
                    for grand_dependency in grand_dependencies:
                        if grand_dependency not in results:
                            results.append(grand_dependency)
                return results

            job_status = {
                0: "Unknown",
                1: "Active",
                2: "Suspended",
                3: "Completed",
                4: "Failed",
                6: "Pending"
            }

            jobs_to_validate = [job]
            jobs_to_validate.extend(recursive_dependencies(job))
            failed_jobs = []
            errors = []
            for job in jobs_to_validate:
                if "Failed" == job_status[job["Stat"]]:
                    failed_jobs.append(str(job))

                resp_error = requests.get(
                    "{}/api/jobreports?JobID={}&Data=allerrorcontents".format(
                        deadline_url, job["_id"]
                    ),
                    timeout=10
                )
                errors.extend(resp_error.json())

            msg = "Errors in Deadline:\n"
            msg += "\n".join(errors)
            assert not errors, msg

            msg = "Failed in Deadline:\n"
            msg += "\n".join(failed_jobs)
            assert not failed_jobs, msg

            # '0001-...' returned until job is finished
            valid_date_finished = response.json()[0]["DateComp"][:4] != "0001"

        # some clean exit test possible?
        print("Publish finished")
        yield True


class HostFixtures():
    """Host specific fixtures. Should be implemented once per host."""
    @pytest.fixture(scope="module")
    def last_workfile_path(self, download_test_data, output_folder_url):
        """Returns url of workfile"""
        raise NotImplementedError

    @pytest.fixture(scope="module")
    def startup_scripts(self, monkeypatch_session, download_test_data):
        """"Adds init scripts (like userSetup) to expected location"""
        raise NotImplementedError

    @pytest.fixture(scope="module")
    def skip_compare_folders(self):
        """Use list of regexs to filter out published folders from comparing"""
        raise NotImplementedError

import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.nuke.lib import (
    NukeDeadlinePublishTestClass
)

log = logging.getLogger("test_publish_in_nuke")


class TestDeadlinePublishInNuke(NukeDeadlinePublishTestClass):
    """Basic test case for publishing in Nuke

        Uses generic TestCase to prepare fixtures for test data, testing DBs,
        env vars.

        !!!
        It expects modified path in WriteNode,
        use '[python {nuke.script_directory()}]' instead of regular root
        dir (eg. instead of `c:/projects`).
        Access file path by selecting WriteNode group, CTRL+Enter, update file
        input
        !!!

        Opens Nuke, run publish on prepared workile.

        Then checks content of DB (if subset, version, representations were
        created.
        Checks tmp folder if all expected files were published.

        How to run:
        (in cmd with activated {AYON_ROOT}/.venv)
        {AYON_ROOT}/.venv/Scripts/python.exe {AYON_ROOT}/start.py
        runtests ../tests/integration/hosts/nuke  # noqa: E501

        To check log/errors from launched app's publish process keep PERSIST
        to True and check `test_ayon.logs` collection.
    """
    TEST_FILES = [
        ("resources/test_deadline_publish_in_nuke.zip",
         "test_deadline_publish_in_nuke.zip", "")
    ]

    APP_GROUP = "nuke"

    TIMEOUT = 240  # publish timeout

    # could be overwritten by command line arguments
    # keep empty to locate latest installed variant or explicit
    APP_VARIANT = ""
    PERSIST = False  # True - keep test_db, test_openpype, outputted test files
    TEST_DATA_FOLDER = None

    def test_db_asserts(self, publish_finished):
        """Host and input data dependent expected results in DB."""
        print("test_db_asserts")
        failures = []

        project_name = self.PROJECT

        versions = ayon_api.get_versions(project_name)

        not_first_version = [version
                             for version in versions
                             if version["version"] != 1]
        failures.append(
            DBAssert.count_compare(
                "versions",
                not_first_version,
                0
            )
        )
        products = ayon_api.get_products(project_name)
        failures.append(DBAssert.count_compare("products", products, 2))

        products = ayon_api.get_products(project_name,
                                         product_names=["renderTest_taskMain"])
        failures.append(DBAssert.count_compare("render products", products, 1))

        products = ayon_api.get_products(project_name,
                                         product_names=["workfileTest_task"])
        failures.append(
            DBAssert.count_compare("workfile products", products, 1))

        representations = list(ayon_api.get_representations(project_name))
        failures.append(
            DBAssert.count_compare(
                "representations",
                representations,
                4
            )
        )

        workfile_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "workfileTest_task" and
               repre["context"]["ext"] == "nk"
        ]
        failures.append(
            DBAssert.count_compare("workfile representations", workfile_repres,
                                   1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["context"]["ext"] == "exr"
        ]
        failures.append(
            DBAssert.count_compare("render representations", render_repres, 1))

        thumb_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["name"] == "thumbnail"
        ]
        failures.append(
            DBAssert.count_compare("thumbnail representations", thumb_repres,
                                   1))

        burnin_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["name"] == "baking_h264_mov"
        ]
        failures.append(
            DBAssert.count_compare(
                "burnin_repres representations",
                burnin_repres,
                1)
        )

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestDeadlinePublishInNuke()

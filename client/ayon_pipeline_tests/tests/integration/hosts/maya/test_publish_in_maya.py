import re
import os

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.maya.lib import (
    MayaLocalPublishTestClass
)


class TestPublishInMaya(MayaLocalPublishTestClass):
    """Basic test case for publishing in Maya

        Shouldnt be running standalone only via 'runtests' pype command! (??)

        Uses generic TestCase to prepare fixtures for test data, testing DBs,
        env vars.

        Always pulls and uses test data from GDrive!

        Opens Maya, runs publish on prepared workile.

        Then checks content of DB (if subset, version, representations were
        created.
        Checks tmp folder if all expected files were published.

        How to run:
        (in cmd with activated {AYON_ROOT}/.venv)
        {AYON_ROOT}/.venv/Scripts/python.exe {AYON_ROOT}/start.py runtests ../tests/integration/hosts/maya  # noqa: E501

    """
    PERSIST = False

    TEST_FILES = [
        ("test_publish_in_maya", "", "")
    ]

    APP_GROUP = "maya"
    # keep empty to locate latest installed variant or explicit
    APP_VARIANT = ""

    TIMEOUT = 120  # publish timeout

    def test_publish(
        self,
        publish_finished,
        download_test_data
    ):
        """Testing Pyblish and Python logs within Maya."""

        # All maya output via MAYA_CMD_FILE_OUTPUT env var during test run
        logging_path = os.path.join(download_test_data, "output.log")
        with open(logging_path, "r") as f:
            logging_output = f.read()

        print(("-" * 50) + "LOGGING" + ("-" * 50))
        print(logging_output)

        # Check for pyblish errors.
        error_regex = r"pyblish \(ERROR\)((.|\n)*?)((pyblish \())"
        matches = re.findall(error_regex, logging_output)
        assert not matches, matches[0][0]

        # Check for python errors.
        error_regex = r"// Error((.|\n)*)"
        matches = re.findall(error_regex, logging_output)
        assert not matches, matches[0][0]

    def test_db_asserts(self, publish_finished):
        """Host and input data dependent expected results in DB."""
        print("test_db_asserts")
        failures = []
        project_name = self.PROJECT

        versions = list(ayon_api.get_versions(project_name))

        failures.append(
            DBAssert.count_compare(
                "versions",
                versions,
                3
            )
        )

        hero_version = [version
                        for version in versions
                        if version["version"] == -1]
        failures.append(
            DBAssert.count_compare(
                "versions",
                hero_version,
                1
            )
        )

        products = ayon_api.get_products(project_name)
        failures.append(DBAssert.count_compare("products", products, 2))

        products = ayon_api.get_products(project_name,
                                         product_names=["modelMain"])
        failures.append(DBAssert.count_compare("model products", products, 1))

        products = ayon_api.get_products(project_name,
                                         product_names=["workfileTest_task"])
        failures.append(DBAssert.count_compare("wfile products", products, 1))

        # 2 (model) + 2 (hero) + 1 workfile
        representations = list(ayon_api.get_representations(project_name))
        failures.append(
            DBAssert.count_compare(
                "representations",
                representations,
                5
            )
        )

        workfile_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "workfileTest_task" and
               repre["context"]["ext"] == "ma"
        ]
        failures.append(
            DBAssert.count_compare(
                "workfile representations", workfile_repres, 1))

        abc_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "modelMain" and
               repre["context"]["ext"] == "abc"
        ]
        failures.append(
            DBAssert.count_compare(
                "abc representations", abc_repres, 2))

        ma_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "modelMain" and
               repre["context"]["ext"] == "ma"
        ]
        failures.append(
            DBAssert.count_compare(
                "abc representations", ma_repres, 2))

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestPublishInMaya()

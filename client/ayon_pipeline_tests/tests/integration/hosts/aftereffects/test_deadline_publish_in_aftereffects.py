import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.aftereffects.lib import (
    AEDeadlinePublishTestClass)

log = logging.getLogger("test_publish_in_aftereffects")


class TestDeadlinePublishInAfterEffects(AEDeadlinePublishTestClass):
    """Basic test case for DL publishing in AfterEffects

        Uses generic TestCase to prepare fixtures for test data, testing DBs,
        env vars.

        Opens AfterEffects, run DL publish on prepared workile.

        Test zip file sets 3 required env vars:
        - HEADLESS_PUBLISH - this triggers publish immediately app is open
        - AYON_IN_TESTS - this differentiate between regular webpublish
        - PYBLISH_TARGETS

        Waits for publish job on DL is finished.

        Then checks content of DB (if subset, version, representations were
        created.
        Checks tmp folder if all expected files were published.

    """
    PERSIST = False

    TEST_FILES = [
        ("resources/test_deadline_publish_in_aftereffects.zip",
         "test_deadline_publish_in_aftereffects.zip",
         "")
    ]

    APP_GROUP = "aftereffects"
    APP_VARIANT = "2024"

    APP_NAME = "{}/{}".format(APP_GROUP, APP_VARIANT)

    TIMEOUT = 120  # publish timeout

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
                2
            )
        )

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
        failures.append(DBAssert.count_compare("wfile products", products, 1))

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
               repre["context"]["ext"] == "aep"
        ]
        failures.append(
            DBAssert.count_compare(
                "workfile representations", workfile_repres, 1))

        # single frame render results in single frame review (as png not mp4)
        png_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["context"]["ext"] == "png"
        ]
        failures.append(
            DBAssert.count_compare(
                "png representations", png_repres, 2))

        mp4_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["context"]["ext"] == "mp4"
        ]
        failures.append(
            DBAssert.count_compare(
                "mp4 representations", mp4_repres, 0))

        thumb_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["context"]["ext"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare(
                "thumb representations", thumb_repres, 1))

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestDeadlinePublishInAfterEffects()

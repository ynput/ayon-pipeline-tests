import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.aftereffects.lib import AELocalPublishTestClass

log = logging.getLogger("test_publish_in_aftereffects")


class TestPublishInAfterEffects(AELocalPublishTestClass):
    """Basic test case for publishing in AfterEffects

    Should publish 10 frames
    """
    PERSIST = True

    TEST_FILES = [
        ("resources/test_publish_in_aftereffects_multiframe.zip",
         "test_publish_in_aftereffects_multiframe.zip",
         "")
    ]

    APP_GROUP = "aftereffects"
    APP_VARIANT = ""

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

        png_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["context"]["ext"] == "png"
        ]
        failures.append(
            DBAssert.count_compare(
                "png representations", png_repres, 1))

        mp4_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain" and
               repre["context"]["ext"] == "mp4"
        ]
        failures.append(
            DBAssert.count_compare(
                "mp4 representations", mp4_repres, 1))

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
    test_case = TestPublishInAfterEffects()

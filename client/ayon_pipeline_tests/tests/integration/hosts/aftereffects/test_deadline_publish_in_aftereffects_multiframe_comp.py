import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.aftereffects.lib import AEDeadlinePublishTestClass


class TestDeadlinePublishInAfterEffectsMultiComposition(AEDeadlinePublishTestClass):  # noqa
    """Test case for DL publishing in AfterEffects with multiple compositions.

        Workfile contains 2 prepared `render` instances. First has review set,
        second doesn't.

        Uses generic TestCase to prepare fixtures for test data, testing DBs,
        env vars.

        Opens AfterEffects, run DL publish on prepared workile.

        Test zip file sets 3 required env vars:
        - HEADLESS_PUBLISH - this triggers publish immediately app is open
        - AYON_IN_TESTS - this differentiate between regular webpublish
        - PYBLISH_TARGETS

        As there are multiple render and publish jobs, it waits for publish job
        of later render job. Depends on date created of metadata.json.

        Then checks content of DB (if product, version, representations were
        created.

    """
    PERSIST = False

    TEST_FILES = [
        ("resources/test_deadline_publish_in_aftereffects_multiframe_comp.zip",
         "test_deadline_publish_in_aftereffects_multiframe_comp.zip",
         "")
    ]

    APP_GROUP = "aftereffects"
    APP_VARIANT = "2024"

    APP_NAME = "{}/{}".format(APP_GROUP, APP_VARIANT)

    TIMEOUT = 300  # publish timeout

    def test_db_asserts(self, publish_finished):
        """Host and input data dependent expected results in DB."""
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
        failures.append(DBAssert.count_compare("products", products, 3))

        products = ayon_api.get_products(project_name,
                                         product_names=["renderTest_taskMain"])
        failures.append(DBAssert.count_compare("render products", products, 1))

        products = ayon_api.get_products(project_name,
                                         product_names=["renderTest_taskMain2"])
        failures.append(DBAssert.count_compare("render2 products", products, 1))

        products = ayon_api.get_products(project_name,
                                         product_names=["workfileTest_task"])
        failures.append(DBAssert.count_compare("wfile products", products, 1))

        representations = list(ayon_api.get_representations(project_name))
        failures.append(
            DBAssert.count_compare(
                "representations",
                representations,
                6
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

        exr_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain2" and
               repre["context"]["ext"] == "exr"
        ]
        failures.append(
            DBAssert.count_compare(
                "exr representations", exr_repres, 1))

        # no review for renderTest_taskMain2 >> no mp4
        mp4_repres2 = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain2" and
               repre["context"]["ext"] == "mp4"
        ]
        failures.append(
            DBAssert.count_compare(
                "mp4 taskMain2 representations", mp4_repres2, 0))

        # since ayon-core/pull/1251 - thumbnail will be created
        thumb_repres2 = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain2" and
               repre["context"]["ext"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare(
                "thumb_repres2 representations", thumb_repres2, 1))

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestDeadlinePublishInAfterEffectsMultiComposition()

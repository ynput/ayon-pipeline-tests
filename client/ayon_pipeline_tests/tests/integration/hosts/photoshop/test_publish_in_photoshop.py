import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.photoshop.lib import (
    PhotoshopTestClass
)


class TestPublishInPhotoshop(PhotoshopTestClass):
    """Basic test case for publishing in Photoshop

    Uses generic TestCase to prepare fixtures for test data, testing DBs,
    env vars.

    Opens Photoshop, run publish on prepared workile.

    Test zip file sets 3 required env vars:
    - HEADLESS_PUBLISH - this triggers publish immediately app is open
    - AYON_IN_TESTS - this differentiate between regular webpublish
    - PYBLISH_TARGETS

    Always pulls and uses test data from GDrive!

    Test zip file sets 3 required env vars:
    - HEADLESS_PUBLISH - this triggers publish immediately app is open
    - AYON_IN_TESTS - this differentiate between regular webpublish
    - PYBLISH_TARGETS

    Then checks content of DB (if product, version, representations were
    created.
    Checks tmp folder if all expected files were published.

    How to run:
    (in cmd with activated {AYON_ROOT}/.venv)
    {AYON_ROOT}/.venv/Scripts/python.exe {AYON_ROOT}/start.py runtests ../tests/integration/hosts/photoshop  # noqa: E501

    """
    PERSIST = True

    TEST_FILES = [
        ("resources/test_publish_in_photoshop.zip",
         "test_publish_in_photoshop.zip", "")
    ]

    APP_GROUP = "photoshop"
    # keep empty to locate latest installed variant or explicit
    APP_VARIANT = ""

    APP_NAME = "{}/{}".format(APP_GROUP, APP_VARIANT)

    TIMEOUT = 120  # publish timeout

    def test_db_asserts(self, publish_finished):
        """Host and input data dependent expected results in DB."""
        project_name = self.PROJECT
        failures = []

        versions = ayon_api.get_versions(project_name)
        failures.append(DBAssert.count_compare("versions", versions, 4))

        not_first_version = [version
                             for version in versions
                             if version["version"] != 1]
        failures.append(
            DBAssert.count_compare(
                "not first versions",
                not_first_version,
                0
            )
        )
        products = ayon_api.get_products(project_name)
        failures.append(DBAssert.count_compare("products", products, 4))

        products = ayon_api.get_products(project_name,
                                         product_names=["imageMainForeground"])
        failures.append(
            DBAssert.count_compare(
                "imageMainForeground products",
                products,
                1
            )
        )

        products = ayon_api.get_products(project_name,
                                         product_names=["imageMainBackground"])
        failures.append(
            DBAssert.count_compare(
                "imageMainBackground products",
                products,
                1
            )
        )

        products = ayon_api.get_products(project_name,
                                         product_names=["review"])
        failures.append(
            DBAssert.count_compare(
                "review products",
                products,
                1
            )
        )

        products = ayon_api.get_products(project_name,
                                         product_names=["workfileTest_task"])
        failures.append(
            DBAssert.count_compare("workfile products", products, 1))

        representations = list(ayon_api.get_representations(project_name))
        failures.append(
            DBAssert.count_compare(
                "representations",
                representations,
                8
            )
        )

        workfile_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "workfileTest_task" and
               repre["context"]["ext"] == "psd"
        ]
        failures.append(
            DBAssert.count_compare("workfile representations", workfile_repres,
                                   1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["context"]["ext"] == "png"
        ]
        failures.append(
            DBAssert.count_compare("MainForeground representations",
                                   render_repres, 1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["context"]["ext"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare("MainForeground representations",
                                   render_repres, 1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["context"]["ext"] == "tga"
        ]
        failures.append(
            DBAssert.count_compare("MainForeground representations",
                                   render_repres, 1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainBackground" and
               repre["context"]["ext"] == "png"
        ]
        failures.append(
            DBAssert.count_compare("MainBackground representations",
                                   render_repres, 1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainBackground" and
               repre["context"]["ext"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare("MainBackground representations",
                                   render_repres, 1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainBackground" and
               repre["context"]["ext"] == "tga"
        ]
        failures.append(
            DBAssert.count_compare("MainBackground representations",
                                   render_repres, 1))

        thumb_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["name"] == "thumbnail"
        ]
        failures.append(
            DBAssert.count_compare("thumbnail representations", thumb_repres,
                                   0))

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestPublishInPhotoshop()

import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.photoshop.lib import (
    PhotoshopTestClass
)


class TestPublishInPhotoshopImageReviews(PhotoshopTestClass):
    """Test for publish in Phohoshop with different review configuration.

    Workfile contains 2 image instance, one has review flag, second doesn't.

    Regular `review` family is disabled.

    Expected result is to `imageMainForeground` to have additional file with
    review, `imageMainBackground` without. No separate `review` family.

    `test_project_test_asset_imageMainForeground_v001_jpg.jpg` is expected name
    of imageForeground review, `_jpg` suffix is needed to differentiate between
    image and review file.

    """
    PERSIST = True

    TEST_FILES = [
        ("resources/test_publish_in_photoshop_review.zip",
         "test_publish_in_photoshop_review.zip", "")
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
        failures.append(DBAssert.count_compare("versions", versions, 3))

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
        failures.append(DBAssert.count_compare("products", products, 3))

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
                                         product_names=["workfileTest_task"])
        failures.append(
            DBAssert.count_compare("workfile products", products, 1))

        representations = list(ayon_api.get_representations(project_name))
        failures.append(
            DBAssert.count_compare(
                "representations",
                representations,
                6
            )
        )

        products = ayon_api.get_products(project_name,
                                         product_names=["review"])
        failures.append(
            DBAssert.count_compare(
                "review products",
                products,
                0
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
            DBAssert.count_compare("MainForeground png representations",
                                   render_repres, 1))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["context"]["ext"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare("MainForeground jpg representations",
                                   render_repres, 2))

        render_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["context"]["ext"] == "jpg" and
               repre["name"] == "jpg_jpg"
        ]
        failures.append(
            DBAssert.count_compare("FG review representations", render_repres,
                                   1))

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
            DBAssert.count_compare("MainBackground jpg representations",
                                   render_repres, 2))

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
    test_case = TestPublishInPhotoshopImageReviews()

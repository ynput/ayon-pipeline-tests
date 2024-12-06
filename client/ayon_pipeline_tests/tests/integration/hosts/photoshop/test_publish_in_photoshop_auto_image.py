import logging

import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.photoshop.lib import PhotoshopTestClass


class TestPublishInPhotoshopAutoImage(PhotoshopTestClass):
    """Test for publish in Photoshop with different review configuration.

    Workfile contains 3 layers, auto image and review instances created.

    Test contains updates to addon Settings!!!

    """
    PERSIST = True

    TEST_FILES = [
        ("resources/test_publish_in_photoshop_auto_image.zip",
         "test_publish_in_photoshop_auto_image.zip", "")
    ]

    APP_GROUP = "photoshop"
    # keep empty to locate latest installed variant or explicit
    APP_VARIANT = ""

    APP_NAME = "{}/{}".format(APP_GROUP, APP_VARIANT)

    TIMEOUT = 120  # publish timeout

    def update_addon_versions(self):
        """Implement changes of current addon version from version in dump."""
        old_version = "0.2.2"
        addon_name = "photoshop"
        project_name = self.PROJECT
        bundles = ayon_api.get_bundles()

        production_bundle = None
        for bundle in bundles["bundles"]:
            if bundle["name"] == bundles["productionBundle"]:
                production_bundle = bundle
                break

        current_version = production_bundle["addons"].get(addon_name)

        if not current_version:
            raise RuntimeError(f"{addon_name} not set in production bundle")

        endpoint = f"addons/{addon_name}/{old_version}/rawOverrides/{project_name}"
        response = ayon_api.get(endpoint)
        response.raise_for_status()
        raw_addon_settings = response.data

        if raw_addon_settings:
            self.log.debug(f"Creating new settings for {current_version}")
            endpoint = f"addons/{addon_name}/{current_version}/rawOverrides/{project_name}"
            response = ayon_api.put(endpoint, **raw_addon_settings)
            response.raise_for_status()

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
                0
            )
        )

        products = ayon_api.get_products(project_name,
                                         product_names=["imageMainBackground"])
        failures.append(
            DBAssert.count_compare(
                "imageMainBackground products",
                products,
                0
            )
        )

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
               repre["context"]["ext"] == "psd"
        ]
        failures.append(
            DBAssert.count_compare("workfile representations", workfile_repres,
                                   1))

        # because no imageMainForeground instance in workfile
        imageFG_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageMainForeground" and
               repre["context"]["ext"] == "png"
        ]
        failures.append(
            DBAssert.count_compare("MainForeground png representations",
                                   imageFG_repres, 0))

        # auto (or flatten) image because of enabled ayon+settings://photoshop/create/AutoImageCreator?project=test_project
        # with `Review by Default` and Beauty Default variant
        auto_image_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageBeauty" and
               repre["context"]["ext"] == "png" and
               repre["name"] == "png"
        ]
        failures.append(
            DBAssert.count_compare("auto image representations",
                                   auto_image_repres, 1))

        auto_image_review_thumb_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageBeauty" and
               repre["context"]["ext"] == "jpg" and
               repre["name"] == "jpg_jpg"
        ]
        failures.append(
            DBAssert.count_compare("auto image review representations",
                                   auto_image_review_thumb_repres, 1))

        auto_image_review_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "imageBeauty" and
               repre["context"]["ext"] == "jpg" and
               repre["name"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare("auto_image_review_repres representations",
                                   auto_image_review_repres, 1))

        # separate review because of ayon+settings://photoshop/create/ReviewCreator?project=test_project
        # with empty Default Variants
        review_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "review"
        ]
        failures.append(
            DBAssert.count_compare("review_repres representations",
                                   review_repres, 1))

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestPublishInPhotoshopAutoImage()

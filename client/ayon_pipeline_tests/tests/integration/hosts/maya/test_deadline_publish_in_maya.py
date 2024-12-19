import ayon_api

from ayon_pipeline_tests.tests.lib.assert_classes import DBAssert
from ayon_pipeline_tests.tests.integration.hosts.maya.lib import (
    MayaDeadlinePublishTestClass
)


class TestDeadlinePublishInMaya(MayaDeadlinePublishTestClass):
    """Basic test case for publishing in Maya

        Opens Maya, runs publish on prepared workile.

        Sends file to be rendered on Deadline.

        Then checks content of DB (if product, version, representations were
        created.
        Checks tmp folder if all expected files were published.

        How to run:
        (in cmd with activated {AYON_ROOT}/.venv)
        {AYON_ROOT}/.venv/Scripts/python.exe {AYON_ROOT}/start.py addon pipeline_tests runtests ../tests/integration/hosts/maya  # noqa: E501

        TODO: temporarily disabled ValidateRenderImageRule because https://github.com/ynput/ayon-maya/issues/194
           - remove update to project_test_project.settings in DB dump
           - remove update_addon_versions
    """
    PERSIST = False

    TEST_FILES = [
        ("test_deadline_publish_in_maya", "", "")
    ]

    APP_GROUP = "maya"
    # keep empty to locate latest installed variant or explicit
    APP_VARIANT = ""

    TIMEOUT = 240  # publish timeout

    def update_addon_versions(self):
        """Implement changes of current addon version from version in dump."""
        version_stored_in_db = "0.2.4"
        addon_name = "maya"
        project_name = self.PROJECT

        self._update_addon_versions(
            project_name, addon_name, version_stored_in_db)

    def test_db_asserts(self, publish_finished):
        """Host and input data dependent expected results in DB."""
        failures = []
        project_name = self.PROJECT

        # versions
        versions = list(ayon_api.get_versions(project_name))

        # model + workfile + render + hero model
        failures.append(
            DBAssert.count_compare(
                "versions",
                versions,
                4
            )
        )

        # hero version is -1
        not_first_version = [version
                             for version in versions
                             if version["version"] != 1]
        failures.append(
            DBAssert.count_compare(
                "versions",
                not_first_version,
                1
            )
        )

        # products
        products = ayon_api.get_products(project_name)
        failures.append(DBAssert.count_compare("products", products, 3))

        products = ayon_api.get_products(
            project_name, product_names=["modelMain"])
        failures.append(DBAssert.count_compare("model products", products, 1))

        products = ayon_api.get_products(
            project_name, product_names=["renderTest_taskMain_beauty"])
        failures.append(DBAssert.count_compare("model products", products, 1))

        products = ayon_api.get_products(
            project_name, product_names=["workfileTest_task"])
        failures.append(DBAssert.count_compare("wfile products", products, 1))

        # representations
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

        exr_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain_beauty" and
               repre["context"]["ext"] == "exr"
        ]
        failures.append(
            DBAssert.count_compare(
                "exr representations", exr_repres, 1))

        mp4_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain_beauty" and
               repre["context"]["ext"] == "mp4"
        ]
        failures.append(
            DBAssert.count_compare(
                "mp4 representations", mp4_repres, 1))

        thumb_repres = [
            repre
            for repre in representations
            if repre["context"]["product"]["name"] == "renderTest_taskMain_beauty" and
               repre["context"]["ext"] == "jpg"
        ]
        failures.append(
            DBAssert.count_compare(
                "thumb representations", thumb_repres, 1))

        assert not any(failures)


if __name__ == "__main__":
    test_case = TestDeadlinePublishInMaya()

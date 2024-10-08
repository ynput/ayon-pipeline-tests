"""Test file for Sync Server, tests API methods, currently for integrate_new

    File:
        creates temporary directory and downloads .zip file from GDrive
        unzips .zip file
        uses content of .zip file (MongoDB's dumps) to import to new databases
        with use of 'monkeypatch_session' modifies required env vars
            temporarily
        runs battery of tests checking that site operation for Sync Server
            module are working
        removes temporary folder
        removes temporary databases (?)
"""
import pytest

from ayon_pipeline_tests.tests.lib.testing_classes import ModuleUnitTest


class TestModuleApi(ModuleUnitTest):

    REPRESENTATION_ID = "60e578d0c987036c6a7b741d"

    TEST_FILES = [("1eCwPljuJeOI8A3aisfOIBKKjcmIycTEt",
                   "test_site_operations.zip", '')]

    @pytest.fixture(scope="module")
    def setup_sitesync_addon(self):
        """Get sync_server_module from ModulesManager"""
        from ayon_core.addon import AddonsManager

        manager = AddonsManager()
        sitesync = manager.addons_by_name["sitesync"]
        yield sitesync

    def test_get_alt_site_pairs(self, setup_sitesync_addon):
        conf_sites = {"SFTP": {"alternative_sites": ["studio"]},
                      "studio2": {"alternative_sites": ["studio"]}}

        ret = setup_sitesync_addon._get_alt_site_pairs(conf_sites)
        expected = {"SFTP": {"studio", "studio2"},
                    "studio": {"SFTP", "studio2"},
                    "studio2": {"studio", "SFTP"}}
        assert ret == expected, "Not matching result"

    def test_get_alt_site_pairs_deep(self, setup_sitesync_addon):
        conf_sites = {"A": {"alternative_sites": ["C"]},
                      "B": {"alternative_sites": ["C"]},
                      "C": {"alternative_sites": ["D"]},
                      "D": {"alternative_sites": ["A"]},
                      "F": {"alternative_sites": ["G"]},
                      "G": {"alternative_sites": ["F"]},
                      }

        ret = setup_sitesync_addon._get_alt_site_pairs(conf_sites)
        expected = {"A": {"B", "C", "D"},
                    "B": {"A", "C", "D"},
                    "C": {"A", "B", "D"},
                    "D": {"A", "B", "C"},
                    "F": {"G"},
                    "G": {"F"}}
        assert ret == expected, "Not matching result"


test_case = TestModuleApi()

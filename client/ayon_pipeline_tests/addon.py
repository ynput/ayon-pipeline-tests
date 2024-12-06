import os
from ayon_core.addon import (
    click_wrap,
    AYONAddon,
)

MY_STUDIO_ADDON_ROOT = os.path.dirname(os.path.abspath(__file__))
ADDON_NAME = "pipeline_tests"
ADDON_LABEL = "Integration tests for AYON"


class PipelineTestsAddon(AYONAddon):
    name = ADDON_NAME
    label = ADDON_LABEL

    # Add CLI
    def cli(self, click_group):
        click_group.add_command(cli_main.to_click_obj())

    @classmethod
    def run_tests(
        cls,
        folder,
        mark,
        pyargs,
        test_data_folder,
        persist,
        app_variant,
        timeout,
        setup_only,
        mongo_url,
        app_group,
        dump_databases
    ):
        """
        Runs tests from 'folder'

        Args:
             folder (str): relative path to folder with tests
             mark (str): label to run tests marked by it (slow etc)
             pyargs (str): package path to test
             test_data_folder (str): url to unzipped folder of test data
             persist (bool): True if keep test db and published after test
                end
            app_variant (str): variant (eg 2020 for AE), empty if use
                latest installed version
            timeout (int): explicit timeout for single test
            setup_only (bool): if only preparation steps should be
                triggered, no tests (useful for debugging/development)
            mongo_url (str): url to Openpype Mongo database
        """
        print("run_tests")
        if folder:
            folder = " ".join(list(folder))
        else:
            folder = "../tests"

        # disable warnings and show captured stdout even if success
        args = [
            "--disable-pytest-warnings",
            "--capture=sys",
            "--print",
            "-W ignore::DeprecationWarning",
            "-rP",
            "-s",
            folder
        ]

        if mark:
            args.extend(["-m", mark])

        if pyargs:
            args.extend(["--pyargs", pyargs])

        if test_data_folder:
            args.extend(["--test_data_folder", test_data_folder])

        if persist:
            args.extend(["--persist", persist])

        if app_group:
            args.extend(["--app_group", app_group])

        if app_variant:
            args.extend(["--app_variant", app_variant])

        if timeout:
            args.extend(["--timeout", timeout])

        if setup_only:
            args.extend(["--setup_only", setup_only])

        if mongo_url:
            args.extend(["--mongo_url", mongo_url])

        if dump_databases:
            msg = "dump_databases format is not recognized: {}".format(
                dump_databases
            )
            assert dump_databases in ["bson", "json"], msg
            args.extend(["--dump_databases", dump_databases])

        print("run_tests args: {}".format(args))
        import pytest
        return pytest.main(args)


@click_wrap.group(
    PipelineTestsAddon.name,
    help="PipelineTestsAddon related commands.")
def cli_main():
    print("<<<< PipelineTestsAddon CLI >>>>")


@cli_main.command()
@click_wrap.argument("folder", nargs=-1)
@click_wrap.option("-m",
              "--mark",
              help="Run tests marked by",
              default=None)
@click_wrap.option("-p",
              "--pyargs",
              help="Run tests from package",
              default=None)
@click_wrap.option("-t",
              "--test_data_folder",
              help="Unzipped directory path of test file",
              default=None)
@click_wrap.option("-s",
              "--persist",
              help="Persist test DB and published files after test end",
              default=None)
@click_wrap.option("-a",
              "--app_variant",
              help="Provide specific app variant for test, empty for latest",
              default=None)
@click_wrap.option("--app_group",
              help="Provide specific app group for test, empty for default",
              default=None)
@click_wrap.option("-t",
              "--timeout",
              help="Provide specific timeout value for test case",
              default=None)
@click_wrap.option("-so",
              "--setup_only",
              help="Only create dbs, do not run tests",
              default=None)
@click_wrap.option("--mongo_url",
              help="MongoDB for testing.",
              default=None)
@click_wrap.option("--dump_databases",
              help="Dump all databases to data folder.",
              default=None)
def runtests(folder, mark, pyargs, test_data_folder, persist, app_variant,
             timeout, setup_only, mongo_url, app_group, dump_databases):
    """Run all automatic tests after proper initialization via start.py"""
    return_code = PipelineTestsAddon.run_tests(
        folder,
        mark,
        pyargs,
        test_data_folder,
        persist,
        app_variant,
        timeout,
        setup_only,
        mongo_url,
        app_group,
        dump_databases
    )

    if bool(return_code):
        raise RuntimeError("Test failed")

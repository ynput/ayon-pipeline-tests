"""Dummy environment that allows importing Openpype modules and run
tests in parent folder and all subfolders manually from IDE.

This should not get triggered if the tests are running from `runtests` as it
is expected there that environment is handled by OP itself.

This environment should be enough to run simple `BaseTest` where no
external preparation is necessary (eg. no prepared DB, no source files).
These tests might be enough to import and run simple pyblish plugins to
validate logic.

Please be aware that these tests might use values in real databases, so use
`BaseTest` only for logic without side effects or special configuration. For
these there is `tests.lib.testing_classes.ModuleUnitTest` which would setup
proper test DB (but it requires `mongorestore` on the sys.path)

If pyblish plugins require any host dependent communication, it would need
 to be mocked.

This setting of env vars is necessary to run before any imports of OP code!
(This is why it is in `conftest.py` file.)
If your test requires any additional env var, copy this file to folder of your
test, it should only that folder.
"""

import os


if not os.environ.get("AYON_IN_TESTS"):  # running tests from cmd or CI
    import os

    os.environ["USE_AYON_SERVER"] = "1"
    os.environ["AYON_SERVER_URL"] = "http://localhost:5000"
    os.environ["AYON_API_KEY"] = "XXXXXX"
    os.environ["AYON_PROJECT_NAME"] = "ayon_test"
    os.environ["AYON_FOLDER_PATH"] = "/assets/characters/characterA"

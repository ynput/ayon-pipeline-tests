Automatic tests for AYON
============================

Requirements:
============

Structure:
- integration - end to end tests, slow (see README.md in the integration folder for more info)
    - openpype/modules/MODULE_NAME - structure follow directory structure in code base
        - fixture - sample data `(MongoDB dumps, test files etc.)`
        - `tests.py` - single or more pytest files for MODULE_NAME
- unit - quick unit test
    - MODULE_NAME
        - fixture
        - `tests.py`

How to run
----------
- activate `{AYON_ROOT}/.venv`
- run in cmd
`{AYON_ROOT}/.venv/Scripts/python.exe {AYON_ROOT}/start.py addon pipeline_tests runtests {AYON_ROOT}/tests/integration`
  - add `hosts/APP_NAME` after integration part to limit only on specific app (eg. `{AYON_ROOT}/tests/integration/hosts/maya`)

OR can use built executables
`ayon_console addon pipeline_tests runtests {ABS_PATH}/tests/integration`

Run in IDE:
-----------
If you prefer to run/debug single file directly in IDE of your choice, you might encounter issues with imports.

In some cases your tests might be so localized, that you don't care about all env vars to be set properly.
In that case you might add this dummy configuration BEFORE any imports in your test file
```
import os
os.environ["USE_AYON_SERVER"] = "1"
os.environ["AYON_SERVER_URL"] = "http://localhost:5000"
os.environ["AYON_API_KEY"] = "XXXXXX"
os.environ["AYON_PROJECT_NAME"] = "ayon_test"
os.environ["AYON_FOLDER_PATH"] = "/assets/characters/characterA"
```
If you would like to test specific bundle add these:
```
os.environ["AYON_USE_DEV"] = "1"
os.environ["AYON_BUNDLE_NAME"] = "YOUR_DEV_BUNDLE"
```

You might also like to add this if you would like to use Local Settings for particular site:
```
os.environ["AYON_SITE_ID"] = "YOUR_SITE_ID"
```

This might be enough to run your test file separately. Do not commit this skeleton though.
Use only when you know what you are doing!

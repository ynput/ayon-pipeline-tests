Integration test for AYON
=============================
Contains end-to-end tests for automatic testing of OP.

Should run headless publish on all hosts to check basic publish use cases automatically
to limit regression issues.

Uses env var `HEADLESS_PUBLISH` (set in test data zip files) to differentiate between regular publish
and "automated" one.

How to run
----------
- activate `{AYON_ROOT}/.venv`
- run in cmd
`{AYON_ROOT}/.venv/Scripts/python.exe {AYON_ROOT}/start.py addon pipeline_tests runtests {AYON_ROOT}/tests/integration`
  - add `hosts/APP_NAME` after integration part to limit only on specific app (eg. `{AYON_ROOT}/tests/integration/hosts/maya`)

OR can use built executables
`ayon_console addon pipeline_tests runtests {ABS_PATH}/tests/integration`

Command line arguments
----------------------
 - "--mark" - "Run tests marked by",
 - "--pyargs" - "Run tests from package",
 - "--test_data_folder" - "Unzipped directory path of test file",
 - "--persist" - "Persist test DB and published files after test end",
 - "--app_variant" - "Provide specific app variant for test, empty for latest",
 - "--app_group" - "Provide specific app group for test, empty for default",
 - "--timeout" - "Provide specific timeout value for test case",
 - "--setup_only" - "Only create dbs, do not run tests",

You should see only test asset and state of databases for that particular use case.

How to check logs/errors from app
--------------------------------
Keep PERSIST to True in the class or via `--persist` command line.

How to create test for publishing from host
------------------------------------------
- Extend PublishTest in `tests/lib/testing_classes.py`
- Use `resources\test_data.zip` skeleton file as a template for testing input data
- Create subfolder `test_data` with matching name to your test file containing you test class
  - (see `tests/integration/hosts/maya/test_publish_in_maya` and `test_publish_in_maya.py`)
- Put this subfolder name into TEST_FILES [(HASH_ID, FILE_NAME, MD5_OPTIONAL)]
  - at first position, all others may be ""
- Put workfile into `test_data/input/workfile`
- If you require other than base DB dumps provide them to `test_data/input/dumps`
-- (Check commented code in `db_handler.py` how to dump specific DB. Currently all collections will be dumped.
-   OR if you have access to `ayon-docker` use there `./manage.ps1 dump test_project`)
- Implement `last_workfile_path`
- `startup_scripts` - must contain pointing host to startup script saved into `test_data/input/startup`
  -- Script must contain something like (pseudocode)
```
import pyblish.util
pyblish.util.publish()
```

- If you would like add any command line arguments for your host app add it to `test_data/input/app_args/app_args.json` (as a json list)
- Provide any required environment variables to `test_data/input/env_vars/env_vars.json` (as a json dictionary)
- Implement any assert checks you need in extended class
- Run test class manually (via Pycharm or pytest runner (TODO))
- If you want test to visually compare expected files to published one, set PERSIST to True, run test manually
  -- Locate temporary `publish` subfolder of temporary folder (found in debugging console log)
  -- Copy whole folder content into .zip file into `expected` subfolder
  -- By default tests are comparing only structure of `expected` and published format (eg. if you want to save space, replace published files with empty files, but with expected names!)
  -- Zip and upload again, change PERSIST to False

- Use `TEST_DATA_FOLDER` variable in your class to reuse existing downloaded and unzipped test data (for faster creation of tests)
- Keep `APP_VARIANT` empty if you want to trigger test on latest version of app, or provide explicit value (as '2022' for Photoshop for example)

For storing test zip files on Google Drive:
- Zip `test_data.zip`, named it with descriptive name, upload it to Google Drive, right click - `Get link`, copy hash id (file must be accessible to anyone with a link!)
- Put this hash id and zip file name into TEST_FILES [(HASH_ID, FILE_NAME, MD5_OPTIONAL)]. If you want to check MD5 of downloaded
file, provide md5 value of zipped file.

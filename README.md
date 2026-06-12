# README.md

- [README.md](#readmemd)
  - [Introduction](#introduction)
  - [Directory structure](#directory-structure)
    - [Why is used directory "src"? Is it possible to use real project root? What is the benefit to use "src"?](#why-is-used-directory-src-is-it-possible-to-use-real-project-root-what-is-the-benefit-to-use-src)
  - [Imports](#imports)
  - [Poetry driven project](#poetry-driven-project)
    - [Prerequisites.](#prerequisites)
      - [Installing pipx.](#installing-pipx)
      - [Installing Poetry.](#installing-poetry)
    - [Installing Poetry driven project.](#installing-poetry-driven-project)
    - [Building distributions.](#building-distributions)
  - [Configuration system.](#configuration-system)
    - [Configuration Hierarchy (Visual)](#configuration-hierarchy-visual)
  - [Version information](#version-information)
    - [Versions](#versions)
    - [Print version information](#print-version-information)
  - [Logger](#logger)
  - [Unit tests](#unit-tests)
    - [Configuration](#configuration)
    - [Running tests](#running-tests)
    - [Writing Unit Tests](#writing-unit-tests)
    - [`__init__.py` in Test Subdirectories (Optional)](#__init__py-in-test-subdirectories-optional)
    - [Customizing Test Discovery](#customizing-test-discovery)
    - [Running tests with test coverage](#running-tests-with-test-coverage)
  - [Start a new project from pymodule](#start-a-new-project-from-pymodule)
  - [Deployment](#deployment)
    - [Preparing packages for different OS.](#preparing-packages-for-different-os)
    - [Setting up local company PyPi server.](#setting-up-local-company-pypi-server)
    - [Client side configuration.](#client-side-configuration)
  - [Installers: pip vs pipx](#installers-pip-vs-pipx)


## Introduction

This project is a simple skeleton of Python importable module which has in addition CLI interface. It uses modern `pyproject.toml` and does not use `setup.py`.

## Directory structure

The directory structure is as follows (this is an example, if in a given project `utils` or `drivers` are not needed, they can be deleted):

```
src
    pymodule    # name of the module, will be used as a name of the directory where the module will be installed
        __init__.py
        # projects sources, distributed in modules
        extensions      # Cython and C extensions (omitted here)
        cli
            # command line entry points
            app.py
        core
            # modules that expose API interface to applications
            __init__.py
            config.py
            core_module_a.py
            core_module_b.py
        include   # directory for headers, specific pymodule, used by C extensions (and Cython extensions?)
        logger
            # application logger
            __init__.py
            logger_module.py
        utils
            __init__.py
            utilities.py
tests
    # test files for modules in other :
    test_core_module_a.py
    test_core_module_b.py
# files at root level:
MANIFEST.in
pyproject.toml
# other files may present here depending on the project
```

### Why is used directory "src"? Is it possible to use real project root? What is the benefit to use "src"?

The use of a `src/` directory in Python projects is commonly adopted but not required. Both approaches—using the `src/` directory or the project root as the source code directory—are considered valid. However, the use of a `src/` directory offers several advantages that make it appealing, particularly for larger or more complex projects.

Why Is the `src/` Directory Used?

1. Prevention of **Accidental Import of Unbuilt Code**: When the project root is used as the source directory (i.e., when the packages and modules are placed at the root of the project), it can result in direct access to the source code during development by being in the current working directory. This may cause potential issues:
  * If scripts or tests are executed from the project root, Python may locate and import the code from the project directory itself instead of from the installed package. This can hide packaging issues (such as missing files in the final distribution) because the local code is being used unknowingly.
  * Confusion during testing may arise, as tests could be inadvertently run against local files rather than the installed package version.

 By placing the code within a src/ directory, Python is forced to look for installed packages rather than directly accessing the project files unless explicitly instructed. This ensures that the code is properly installed and tested in an environment that more closely resembles production.

1. Mitigation of Namespace Clashes: If common names are chosen for the project or modules, such as test.py or setup.py, conflicts may occur if everything is located in the root directory. For instance:

  * The presence of both a `tests/` directory and a `tests.py` file in the root directory could lead to confusion for both Python and external tools.
  * Project-related scripts (like `setup.py` or `manage.py`) could be accidentally imported instead of the actual source code modules.

  The `src/` directory helps to isolate the actual code from the rest of the project structure (such as tests, documentation, or build files), thereby reducing the risk of name collisions.

  1. `Improved Clarity`: A project structure that includes a dedicated `src/` directory makes the location of the actual source code more apparent. This is particularly helpful in larger projects where other directories, such as `docs/`, `tests/`, or `ci/`, may exist at the root level. The source code is better organized when separated by the `src/` directory.

## Imports

Depending on the project, one can organize exposition of packages' internals differently. In this template project, each directory under `src/` has `__init__.py` file which brings objects from python module files to a package level. This makes the usage of the packages easier - there is no need for an application programmer to know internal structure. See `src/cli/app.py` for how they are used.

## Poetry driven project

### Prerequisites.

Before working with Poetry driven projects, Poetry should be installed. As its documentations say, Poetry must be installed in its own environment. It should not depend on environments which projects being developed use. Also, it not a good idea to install Poetry in the global Python environment. The installation is made easy by [pipx](https://pipx.pypa.io/stable/installation/).

#### Installing pipx.

Ubuntu Linux:
```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

Other Linux
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Windows:
```bash
python -m pip install --user pipx
```

or

```bash
scoop install pipx
pipx ensurepath
```

The option `--user` directs installation for current user.

#### Installing Poetry.

```bash
pipx install poetry
```

This installs Poetry dependencies and builds Cython and C extensions. After installing, you should be able to start Poetry with

```
pypoetry
```

### Installing Poetry driven project.

First take a look at `pyproject.toml`. It is constructed to point to Poetry as a build tool. See comments for additional information.

Installing project in editable mode. Run following command from the root of the project

```bash
poetry install
```

This command will create virtual environment of the project, will install its dependencies and will build extensions.

Running project. This is done by

```bash
poerty run pymodule
```

or

```bash
poetry shell
pymodule
```

The first variant will be deprecated soon. `poetry shell` opens new shell in current terminal with activated the project's virtual environment.

### Building distributions.

Building is executed under Poetry control:

```bash
poetry build
```

This command will produce two files in `dist` directory like these

```bash
-a----     27.11.2024 г.     17:21         218137 pymodule-0.1.0-cp313-cp313-win_amd64.whl
-a----     27.11.2024 г.     17:20         163210 pymodule-0.1.0.tar.gz
```

## Configuration system.

The configuration system of the module is implemented in `core/config.py`. It is organized at four levels:

* default settings, hard-coded in the source of the module
* configuration file, by default `config.toml` in current directory
* system environment variables
* command line options

The line of priority is (lowest) `default settings` -> `configuration file` -> `environment variables` -> `command line options` (highest).

Default configuration is in `pymodule.core.config.py`. Configuration file is in `toml` format. There are lots of information about `toml` files in the Internet.

Application configuration is implemented in `pymodule.core.config` in `class Config`.

The default configuration comes with information about `pymodule` template metadata: template name, version and description. This information can be used by application to know what template it lays on. This information should not be altered. However, new configuration options can be added as needed. The configuration is presented as a `Dict` object `Config.DEFAULT_CONFIG`.

Logging configuration is in `logging`. It can be changed with other values in the configuration file or with CLI option. By now, one option is available - `--verbose`.

Application options consist of two example options - `param` and `param2` from type `int`. They are here to demonstrate the implementation. These options are in configuration options and at CLI.

The configuration supports positional parameters as well.

```bash
pymodule -v input_file.txt output_file.txt --other_option
```

These positional parameters can be added in `config.toml` in `[positionals]` section. Example:

```bash
[positionals]
input_file = "input_from_config.txt"
output_file = "output_from_config.txt"
```

As can be expected, they can appear in OS environment too. See the function `load_config_env` in `config.py`. The `Dict` variable `env_overrides` contains an example of such parameters.

For consistency, each option on command line should have a configuration option in the default configuration and/or the configuration file.

### Configuration Hierarchy (Visual)

Highest priority → Lowest priority:

```
CLI Options        → override everything
    ↑
Environment Vars   → override config.toml & defaults
    ↑
config.toml        → override hardcoded defaults
    ↑
Default Hardcoded  → fallback values
```

## Version information

### Versions

This template project offers two versions:

* version of the template
* version of the application developed based on this template

The version of the template is stored in `config.py` in `Config.DEFAULT_CONFIG'template']['template_version'] as a string. This string should be of type `major.minor.patch`.

The version of the application is in `pyproject.toml` in `[project.version]`:

```toml
[tool.poetry]
name = "name_of_ the _project"
version = "major.minor.patch"
```

Usually, an application programmer should not change template version (and name). It may do this only when upgrades the template the application project lies on.

However, changing application version is up to the team that develop the project, following project's versioning policy.

### Print version information

The version information of the application can be seen when the option `-v` is given at the command line. This version overrides all other options except `--config`. When `-v` presents at the command line the version is printed and the application exits. There is no way the version information to be printed and then the normal program flow to begin. The format is

```application_name major.minor.patch```

There is no way to show / print template version.

## Logger

Logger module is a simple wrapper over the standard logger in `logging` module. It adds two classes

* `class CustomFormatter` that has implementation of `format` member function
* `class StringHandler` that writes log message into a string array.

`CustomFormatter.format` defines the format of the log messages. If needed it can be edited.

`StringHandler` overloads `emit` member function - it stores messages in internal array called `log_messages`. Two new member functions are added: `get_logs` to get the collected log messages and `clear_logs` to clear collected messages.

Each program module that wants to produce log messages must import logger module by

```
from pymodule.logger import getAppLogger
```

Then creating module logger is

```
logger = getAppLogger(__name__)       # Here __name__ may be changed with any hardcoded string.
```

If a module wants to store log messages to a string along to console printing it should import the functions that handle log messages in `StringHandler`:

```
from pymodule.logger import getAppLogger, enableStringHandler, disableStringHandler, getStringLogs, clearStringLogs
```

and to create logger this way

```
logger = getAppLogger(__name__,True)
```

`enableStringHandler`, `disableStringHandler` and `clearStringLogs` are obvious.

`getStringLogs` returns one big string with log messages separated by '\n'. To print them line by line following can be done

```
messages = getStringLogs().split('\n')
for msg in messages:
    print(msg)
```

## Unit tests

### Configuration

Units tests are executed by `pytest` module which have to be installed in the virtual environment of the project. How this is done is given in above sections.

`pytest` automatically finds the tests. To know where to search, following must be given in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Running tests

To run the unit tests, use the following command in the project root:

```
pytest
```

This will discover and run all the test files in the `tests/` directory automatically. `pytest` looks for files starting with `test_` or ending with `_test.py`, and for functions inside those files starting with `test_`.

### Writing Unit Tests

Unit tests are written in the `tests/` directory. For example, if you have a module `src/core/core_module_a.py` that contains a function like this:

```python
# core/core_module_a.py

def hello_from_core_module_a() -> int:
    print(f"Hello from core_module_a")
    return 1
```

The corresponding unit test in `tests/core/test_core_module_a.py` might look like this:

```python
class TestCore_a(unittest.TestCase):
    def test_hello_from_core_module_a(self):
        self.assertEqual(core_module_a.hello_from_core_module_a(),1)
```

It is allowed test files to be organized in subdirectories of `tests/` directory which is convenient for bigger projects. The directory structure under `tests/` can mirror that of `src/`, which can help keep tests organized and easy to navigate as the project grows.

### `__init__.py` in Test Subdirectories (Optional)

Adding an `__init__.py` file in subdirectories is optional in modern versions of Python. If it is needed to treat subdirectories as packages and import code across test files, `__init__.py` files can be included, but `pytest` will discover tests even if they are not present. No additional configuration is needed unless you want to customize the discovery behavior (e.g., you can add `pytest` options in `pyproject.toml` or a `pytest.ini` file).

### Customizing Test Discovery

For more control over test discovery (for example, if there is non-standard naming conventions or have to exclude certain directories), pytest settings in `pyproject.toml` can be customized:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```
This configures `pytest` to:

* Look for test files in the tests directory (`testpaths`).
* Recognize test files with names starting with test_ (`python_files`).
* Discover test classes and functions starting with `Test` and `test_`.

`pytest` has a lot of command-line options. For more information see the online [pytest documentation](https://docs.pytest.org/en/stable/).

### Running tests with test coverage

To run unit tests with test coverage execute following command from the root of the project.

`pytest --cov=.`

Since MS Visual Studio Code 1.94 it is possible to run tests + coverage from left palette, from testing pane. You can run tests, debug tests and run tests with test coverage. Additional value from such running is that Test coverage pane is updated with percents of coverage of each python module + small graphics showing module state. Test explorer show all tests and makes easy to select which tests to execute. Project explorer also have marks about percents for test coverage.

The project must be installed par example with `pip install -e .` to work with tests.

## Start a new project from pymodule

1. Rename `src/pymodule` to `src/my_application_module_name` by

    `git mv pymodule application_module_name`
2. Edit `pyproject.py`. Change `pymodule` to the real application name.
3. Edit other parts of `pyproject.py` as needed for the application.
4. Edit imports in `.py` files to use new `application_module_name`.
5. Everywhere change `pymodule` to the `application_module_name`.
6. Do not change following sections:

    * `[build-system]`
    * `[tool.setuptools]`
    * `[tool.setuptools.packages.find]`
    * `[tool.pytest.ini_options]`

## Deployment

As seen above, two types of distribution packages are produced: `sdist` and `wheel`. These are (example) `pymodule-0.1.0.tar.gz` and `pymodule-0.1.0-cp312-cp312-manylinux_2_39_x86_64.whl`. They can be sent to users and they to install them by `pip install` or `pipx install`.

If possible, they can be uploaded to https://PyPi.org for whole world usage.

### Preparing packages for different OS.

This process depends on whether the application have C/Cython extensions or not. If it does not use such extensions, te work is easy. Just execute
```bash
cd path_to_the root_of_the_project
rm -rf dist build
poetry build
```
This will produce `sdist` and `wheel` packages in `dist` directory. The packages can be used for installing in Windows, Linux, MacOS even they depend on other pckages that have C/Cython extensions.

The situation with application taht have C/Cython extensions is more complicated. Distributable packages Packages must be built on the system they are intended to be installed on. This means that repository shall be `git cloned` to Windows for Windows packages,
to Linux for Linux packages and so on.

Why is it so complicated? Why there are no any-OS packages and there is no cross-OS building?

A wheel contains native binary code (.so, .pyd, .dll). This code is compiled using
* the compiler in the host OS
* the OS ABI (`ABI` = Application Binary Interface. The OS ABI is the set of rules that define how compiled programs interact with the operating system and with other compiled code.)
* the OS's Python runtime

So:
* `Windows` → produces a `win_amd64` wheel
* `Linux` → produces a `manylinux_x86_64` wheel
* `macOS` → produces a `macosx_x86_64` / `arm64` wheel

There is `no built-in mechanism` in Poetry or setuptools to compile code for another OS.

This is by design → cross-compiling Python extension modules is extremely difficult.

### Setting up local company PyPi server.

This task can be completed using [pypiserver](https://pypi.org/project/pypiserver/). `pypiserver` can be run on Linux, Windows, may be on MacOS as well. The documentation of the pypiserver is at https://github.com/pypiserver/pypiserver.

An example how to start pypiserver on Windows is

```bash
set PYTHONHOME=c:\Python\Python313
C:\Python\Python313\Scripts\pypi-server.exe run -p 3011 e:\data\pypi -P e:\data\pypi\passwords.txt
```

Example directory layout of the pypiserver

```
.
│   passwords.txt
│   pypi-start.bat
│
├───mqttms
│       mqttms-3.0.1-cp313-cp313-win_amd64.whl
│       mqttms-3.0.1.tar.gz
│       mqttms-3.1.1-cp313-cp313-win_amd64.whl
│       mqttms-3.1.1.tar.gz
│
├───ota_http_server
│       ota_http_server-2.0.3-cp313-cp313-win_amd64.whl
│       ota_http_server-2.0.3.tar.gz
│
└───pymodule
        pymodule-0.1.0-cp313-cp313-win_amd64.whl
        pymodule-0.1.0.tar.gz
```

### Client side configuration.

Clients should be told that they shall look for packages at the local pypiserver instead of the global `htpps://PyPi.org`.

On Linux:

Create `~/.pip/pip.conf` with content
```conf
[global]
index-url = http://pypi.ourcompany.com/simple
extra-index-url = https://pypi.org/simple
trusted-host = pypi.mycompany.com
```

On Windows:

Create `C:\Users\user\AppData\Roaming\pip\pip.ini` with content:
```conf
[global]
index-url = http://pypi.ourcompany.com/simple
extra-index-url = https://pypi.org/simple
trusted-host = pypi.mycompany.com
```

This file states:
* `pip` to use `http://pypi.ourcompany.com/simple` instead of `https://pypi.org/simple`.
* If the package to be installed is not found on `http://pypi.ourcompany.com/simple` then `https://pypi.org/simple` is used.
* `trusted-host` says that pypi.mycompany.com is a trusted site. Without this command pip will refuse to download packages from `pypi.mycompany.com`.

`pypiserver` can work behind Apache server which plays as reverse-proxy / https front end.

## Installers: pip vs pipx

`pip` is the usual installer of Python packages. However there is a `pipx` and there is reasons tyo use it when appropriate.

Below is a clear rule-of-thumb used in many Python development teams:

✅ **Use pipx for CLI applications**

If the project **produces an executable command`` (a CLI tool), then **pipx is the preferred installer**.

Examples:

* black
* poetry
* httpie
* Any poetry project that defines console scripts

**Why pipx?**

Installs each tool in an **isolated virtual environment**

No dependency conflicts between tools

Commands are exposed directly on PATH

Easy to upgrade/remove a tool cleanly

**If the Poetry project is meant to be used as a CLI tool → use pipx**.

```
pipx install dist/myapp-1.0.0-py3-none-any.whl
```

✅ Use pip when installing a library into a project environment

If your Poetry-managed project is meant to be used **as a library inside another Python environment**, then use pip.

Examples:

* A shared internal company library imported by other apps
* SDKs
* Modules used by other Python code, not end users

Use pip in the target environment:

```
pip install mylib-1.0.0.whl
```

❗ **Important Point About Poetry Projects**

Poetry creates the `wheel` or `sdist`. Once built, the installation method (pip or pipx) does **not** depend on Poetry anymore.

⭐ **Decision Summary**

Type of project | Install with
----------------| ------------
CLI tool (console scripts) | pipx
Library | pip
App used by end-users | pipx unless it’s a GUI app
App used inside another Python app | pip

**If unsure → pipx is safer**

Because it won’t pollute the system Python environment or conflict with other apps.

🖥️ **Why GUI apps are usually not installed with pipx**

`pipx` is designed specifically for **CLI (command-line) tools** that expose *console scripts*. GUI apps usually behave differently:

✔ **GUI apps often:**

* need desktop shortcuts
* need icons
* may require additional non-Python resources
* integrate with the OS
* need to run outside a terminal

…and pipx does **not** handle any of that.

✔ **pipx installs tools inside isolated venvs and exposes only console scripts on PATH**

So a typical GUI app that is launched via:

* a `.exe` wrapper
* a `.desktop` file (Linux)
* a macOS app bundle
* or a script that requires its working directory to include resources

…may not work correctly when installed via pipx, because pipx **doesn’t install GUI launchers** or manage app resources.

👉 **pipx = perfect for CLI utilities**
👉 **pip = fine for GUI apps, but often companies use installers instead (MSI, EXE, DMG)**

🧪 **CLI vs GUI — the core principle**

✔ **CLI app**

* Has an entry in [tool.poetry.scripts]
* Meant to be typed in terminal
* Perfect for pipx

✔ **GUI app**

* Should have an OS-native launcher
* Often uses resources that need a fixed install location
* pipx doesn't handle OS-level integration
* Better installed via pip or a packaged installer

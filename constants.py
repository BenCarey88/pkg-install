"""Constants for pkg scripts."""

import os

# commands
BUILD = "build"
INSTALL = "install"
LIST = "list"
UNINSTALL = "uninstall"

# directories
PKGS_DIR = os.path.join(os.sep, "PythonPath", "my-pkgs")
PKG_BUILDS_DIR = os.path.join(os.sep, "PythonPath", "pkg-builds")
DEV_PKGS_DIR = os.path.join(os.sep, "PythonPath", "dev-pkgs")
DEV_PKG_BUILDS_DIR = os.path.join(os.sep, "PythonPath", "dev-builds")

# filenames
PKG_INFO_FILE_NAME = "pkg-info.json"
VERSION_INFO_FILE_NAME = "version-info.yaml"

# pkg-info keys
NAME_KEY = "name"
VERSION_KEY = "version"
INSTALL_TIME_KEY = "install_time"
BUILD_TIME_KEY = "build_time"
IGNORE_PATTERNS_KEY = "ignore_patterns"
OWNER_KEY = "owner"
DEPENDENCIES_KEY = "dependencies"

# other
DEFAULT_DEV_VERSION = "dev-0.0.0"
DEFAULT_DEV_COMMENT = "default dev version, used for testing"

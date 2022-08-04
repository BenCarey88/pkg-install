"""Util functions for all pkg scripts."""

import json
import os
import six
import shutil
import yaml

from pkg import constants


def prompt_user_confirmation(
        message,
        confirmation_chars=['y', ''],
        accepted_chars=['y','n', '']):
    """Prompt user confirmation.

    Args:
        message (str): message to give user.
        confirmation_char (list(str)): characters that signal confirmation.
        accepted_chars (list(str)): characters required before user can continue.

    Returns:
        (bool): whether or not user has confirmed.
    """
    answer = None
    while answer not in accepted_chars:
        # six.moves.input is called input in python3, raw_input in python2
        answer = six.moves.input(message).lower()
    return answer in confirmation_chars


def print_error(message, *format_args):
    """Print error message to console.

    Args:
        message (str): error message to print.
        format_args (list(str)): additional args to pass to format function.
    """
    print ("[ERROR] " + message.format(*format_args))


def get_package_info_file(package_dir):
    """Get package info file for given package directory.

    Args:
        package_dir (str): directory of package.

    Returns:
        (str): path of package-info file.
    """
    return os.path.join(package_dir, constants.PKG_INFO_FILE_NAME)


def get_package_info(package_dir, print_on_error=True):
    """Get package info dict from package directory.

    Args:
        package_dir (str): directory of package.
        print_on_error (bool): if True, print error if pkg-info isn't found.

    Returns:
        (str or None): path to pkg info file, if it exists and is readable.
        (dict or None): dict from package info file, or None if file couldn't
            be read or doesn't exist.
    """
    pkg_info_file = get_package_info_file(package_dir)
    if not os.path.isfile(pkg_info_file):
        if print_on_error:
            print_error(
                "The directory \n\n\t{0}\n\n is not a package "
                "(it has no pkg-info.json file)\n".format(package_dir)
            )
        return None, None

    with open(pkg_info_file, "r") as file_:
        try:
            return pkg_info_file, json.load(file_)
        except json.decoder.JSONDecodeError:
            if print_on_error:
                print_error(
                    "The pkg-info file is incorrectly formatted:\n\n\t{0}",
                    pkg_info_file,
                )
            return None, None


def get_version_info_file(package_dir):
    """Get version info file for given package directory.

    Args:
        package_dir (str): directory of package.

    Returns:
        (str): path of version-info file.
    """
    return os.path.join(package_dir, constants.VERSION_INFO_FILE_NAME)


def get_version_info(package_dir):
    """Get version info dict from package directory.

    Args:
        package_dir (str): directory of package.

    Returns:
        (str or None): version info file path, if it exists and is readable.
        (dict or None): dict from version info file, or None if file couldn't
            be read or doesn't exist.
    """
    version_info_file = get_version_info_file(package_dir)
    if not os.path.isfile(version_info_file):
        return None, None

    with open(version_info_file, "r") as file_:
        try:
            return version_info_file, yaml.safe_load(file_)
        except yaml.YAMLError:
            return None, None


def copy_package_directory(
        src_dir,
        dest_dir,
        pkg_name,
        extra_ignore_patterns,
        dev_mode,
        force):
    """Copy pkg directory over from src to dest directory.

    Args:
        src_dir (str): path to source directory.
        dest_dir (str): path to destination directory.
        pkg_name (str): name of package.
        extra_ignore_patterns (str): additional patterns to ignore when copying
            over, on top of the standard python ignore patterns.
        dev_mode (str): if True, we're in dev mode.
        force (bool): whether to force overwrite if the dest_dir already
            exists.

    Returns:
        (bool): whether copying was successful.
    """
    if not os.path.isdir(src_dir):
        print_error("{0} is not a valid directory", src_dir)
    if not os.path.isdir(os.path.dirname(dest_dir)):
        print_error("{0} is not a valid directory to write to", dest_dir)
    if os.path.isdir(dest_dir):
        continue_build = force or prompt_user_confirmation(
            "{0}{1} package already exists. Overwrite? [Y|n]".format(
                pkg_name,
                " dev" if dev_mode else ""
            ),
            confirmation_chars=['y', ''],
            accepted_chars=['y', 'n', ''],
        )
        if not continue_build:
            print ("Aborting.")
            return False
        else:
            shutil.rmtree(dest_dir)

    shutil.copytree(
        src_dir,
        dest_dir,
        ignore=shutil.ignore_patterns(
            "*.pyc",
            ".git*",
            "__pycache__",
            *extra_ignore_patterns
        )
    )
    return True

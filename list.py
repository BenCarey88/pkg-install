"""pkg-list command."""

import json
import os
from collections import OrderedDict

from pkg import constants, utils


def add_subparser_command(subparser):
    """Add pkg-install subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    list_command = subparser.add_parser(
        constants.LIST,
        help="list packages",
    )

    list_command.add_argument(
        "pkg_name",
        nargs="?",
        type=str,
        default="",
        help="Package name to list. If not given, perform global list.",
    )
    list_command.add_argument(
        "-p",
        action="store_true",
        help="List pkg installs only (not develop)",
    )
    list_command.add_argument(
        "-d",
        action="store_true",
        help="List develop installs only",
    )


def _format_strings_in_columns(row_tuples, num_cols, min_col_lengths=None):
    """Format rows of strings in column blocks.

    Args:
        row_tuples (list(tuple(str))): List of tuples of strings. All tuples
            are assumed to have the same size as num_cols.
        num_cols (int): The number of columns to arrange output in.
        min_col_lengths (list(int) or None): if given, this is a list of length
            n less than or equal to num_cols, specifying a minimum length for
            each of the first n columns.

    Returns:
        (str): output string to be printed.
    """
    min_col_lengths = min_col_lengths or []
    column_lengths = [
        0 if i >= len(min_col_lengths) else min_col_lengths[i]
        for i in range(max(num_cols, len(min_col_lengths)))
    ]
    for tuple in row_tuples:
        for i in range(num_cols):
            column_lengths[i] = max(column_lengths[i], len(tuple[i]))
    output = ""
    for tuple in row_tuples:
        row_output = " "
        for string, length in zip(tuple, column_lengths):
            row_output += string + " " * (length - len(string) + 4)
        output += row_output + "\n"
    return output


def _get_all_packages_info(directory):
    """Get info for all packages in given directory.

    Args:
        director (str): directory to search for packages in.

    Returns:
        (str): formatted info.
    """
    package_infos = []
    for pkg in os.listdir(directory):
        pkg_info_file = os.path.join(
            directory, pkg, constants.PKG_INFO_FILE_NAME
        )
        if os.path.isfile(pkg_info_file):
            with open(pkg_info_file) as file_:
                try:
                    pkg_info = json.load(file_)
                except json.decoder.JSONDecodeError:
                    utils.print_error(
                        "The pkg-info file is incorrectly formatted:\n\n\t{0}",
                        pkg_info_file,
                    )
                    return
            version = pkg_info.get(constants.VERSION_KEY, "")
            install_time = pkg_info.get(constants.INSTALL_TIME_KEY, "")
            package_infos.append((pkg, version, install_time))
    return _format_strings_in_columns(package_infos, 3)


def _get_package_install_info(directory, pkg_name):
    """Get info for given installed package in given install directory.

    Args:
        directory (str): directory to search for packages in.
        pkg_name (str): name of package to print info for.

    Returns:
        (str or None): info string for package install, if found.
    """
    pkg_dir = os.path.join(directory, pkg_name)
    if not os.path.isdir(pkg_dir):
        return None
    # note that this will print out errors if pkg_info not found:
    _, pkg_info = utils.get_package_info(pkg_dir)
    if not pkg_info:
        return None
    version = pkg_info.get(constants.VERSION_KEY, "[no_version]")
    time = pkg_info.get(constants.INSTALL_TIME_KEY, "")
    return _format_strings_in_columns([(version, time)], 2)


def _get_package_build_info(directory, pkg_name):
    """Get info for given built package in given build directory.

    Args:
        directory (str): directory to search for packages in.
        pkg_name (str): name of package to print info for.

    Returns:
        (str or None): info string for package builds, if found.
    """
    pkg_build_dir = os.path.join(directory, pkg_name)
    if not os.path.isdir(pkg_build_dir):
        return None
    details = []
    for version in reversed(os.listdir(pkg_build_dir)):
        pkg_version_dir = os.path.join(pkg_build_dir, version)
        if not os.path.isdir(pkg_version_dir):
            continue
        # note that this will print out errors if pkg_info not found:
        _, pkg_info = utils.get_package_info(pkg_version_dir)
        if not pkg_info:
            continue
        _, version_info = utils.get_version_info(pkg_version_dir)
        version_comment = version_info.get(version, "")
        if not version_comment and version == constants.DEFAULT_DEV_VERSION:
            version_comment = constants.DEFAULT_DEV_COMMENT
        # allow multiple comments, and only display top one
        if isinstance(version_comment, (list, tuple)):
            version_comment = next(iter(version_comment), "")
        # allow header with subcomments and only display header
        if isinstance(version_comment, (dict, OrderedDict)):
            version_comment = next(iter(version_comment.keys()), "")
        version_comment = "  " + version_comment
        details.append((
            version,
            pkg_info.get(constants.BUILD_TIME_KEY, ""),
            version_comment
        ))
    if details:
        return _format_strings_in_columns(details, 3)
    return None


def main(args):
    """List all installed packages, or details for specified package.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    if args.d and args.p:
        utils.print_error(
            "Only one of -d and -p flags can be passed to pkg list"
        )

    pkg_name = args.pkg_name
    if not pkg_name:
        # Print out details for all packages
        if not args.d:
            print ("\n Packages\n --------")
            print (_get_all_packages_info(constants.PKGS_DIR))
        if not args.p:
            print ("\n Dev Packages\n ------------")
            print (_get_all_packages_info(constants.DEV_PKGS_DIR))
        return

    # otherwise print out details for specific package
    print ("\n " + pkg_name + "\n " + "=" * len(pkg_name))
    
    install_info = _get_package_install_info(
        constants.PKGS_DIR,
        pkg_name
    )
    build_info = _get_package_build_info(
        constants.PKG_BUILDS_DIR,
        pkg_name
    )
    dev_install_info = _get_package_install_info(
        constants.DEV_PKGS_DIR,
        pkg_name
    )
    dev_build_info = _get_package_build_info(
        constants.DEV_PKG_BUILDS_DIR,
        pkg_name
    )
    if not (install_info or build_info or dev_install_info or dev_build_info):
        print ("\n No package of name " + pkg_name + " found\n")
        return

    if not args.d:
        if install_info:
            print ("\n installed\n ---------")
            print (install_info)
        if build_info:
            print ("\n builds\n ------")
            print (build_info)
    if not args.p:
        if dev_install_info:
            print ("\n dev-installed\n -------------")
            print (dev_install_info)
        if dev_build_info:
            print ("\n dev-builds\n ----------")
            print (dev_build_info)

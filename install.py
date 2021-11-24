"""pkg-install command."""

from datetime import datetime
import json
import os
import shutil

from pkg import constants, utils


def add_subparser_command(subparser):
    """Add pkg-install subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    install_command = subparser.add_parser(
        constants.INSTALL,
        help="install a package",
    )

    install_command.add_argument(
        "pkg_name",
        type=str,
        help="Name of package to install",
    )
    install_command.add_argument(
        "version",
        type=str,
        help="Version of package to install",
    )
    install_command.add_argument(
        "-f",
        action="store_true",
        help="force install (don't ask for confirmation if overwriting)",
    )
    install_command.add_argument(
        "-d",
        action="store_true",
        help="install to develop mode",
    )


def main(args):
    """Install package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    if args.d:
        build_dir = constants.DEV_PKG_BUILDS_DIR
        pkgs_dir = constants.DEV_PKGS_DIR
        success_message = "Dev Package Installed Successfully"
    else:
        build_dir = constants.PKG_BUILDS_DIR
        pkgs_dir = constants.PKGS_DIR
        success_message = "Package Installed Successfully"

    pkg_name = args.pkg_name
    pkg_build_dir = os.path.join(build_dir, pkg_name)
    if not os.path.isdir(pkg_build_dir):
        utils.print_error("Package {0} does not exits", pkg_name)
        return

    version = args.version
    pkg_version_dir = os.path.join(pkg_build_dir, version)
    if not os.path.isdir(pkg_version_dir):
        utils.print_error(
            "Package {0} has no version {1} built",
            pkg_name,
            version
        )
        return

    pkg_info_file, pkg_info = utils.get_package_info(pkg_version_dir)
    if (pkg_info.get(constants.NAME_KEY) != pkg_name
            or pkg_info.get(constants.VERSION_KEY) != version):
        utils.print_error(
            "The pkg-info file name or version is incorrect:\n\n\t{0}",
            pkg_info_file,
        )
        return

    dest_dir = os.path.join(pkgs_dir, pkg_name)
    success = utils.copy_package_directory(
        pkg_version_dir,
        dest_dir,
        pkg_name,
        pkg_info.get(constants.IGNORE_PATTERNS_KEY, []),
        args.d,
        args.f,
    )
    if not success:
        return

    dest_pkg_info = utils.get_package_info_file(dest_dir)
    pkg_info[constants.INSTALL_TIME_KEY] = str(datetime.now().replace(microsecond=0))
    with open(dest_pkg_info, "w") as file_:
        json.dump(pkg_info, file_, indent=4)

    print (success_message)

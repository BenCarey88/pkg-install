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
    install_command.add_argument(
        "-pd",
        action="store_true",
        help="install to develop mode, but using pkg builds",
    )


def run_install(pkg_name, version, dev_builds, dev_installs, force):
    """Run build action.

    Args:
        pkg_name (str): name of package to build.
        version (str): version to build.
        dev_builds (bool): whether or not to get builds from dev-builds
            directory.
        dev_installs (bool): whether or not to install to dev directory.
        force (bool): if True, don't ask for confirmation when rewriting.
    """
    if dev_builds:
        build_dir = constants.DEV_PKG_BUILDS_DIR
    else:
        build_dir = constants.PKG_BUILDS_DIR

    if dev_installs:
        pkgs_dir = constants.DEV_PKGS_DIR
        success_message = "Dev Package Installed Successfully"
    else:
        pkgs_dir = constants.PKGS_DIR
        success_message = "Package Installed Successfully"

    pkg_build_dir = os.path.join(build_dir, pkg_name)
    if not os.path.isdir(pkg_build_dir):
        utils.print_error("Package {0} does not exits", pkg_name)
        return

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
        dev_installs,
        force,
    )
    if not success:
        return

    dest_pkg_info = utils.get_package_info_file(dest_dir)
    pkg_info[constants.INSTALL_TIME_KEY] = str(datetime.now().replace(microsecond=0))
    with open(dest_pkg_info, "w") as file_:
        json.dump(pkg_info, file_, indent=4)

    print (success_message)


def main(args):
    """Install package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    dev_builds = args.d and not args.pd
    dev_installs = args.d or args.pd
    run_install(
        args.pkg_name,
        args.version,
        dev_builds,
        dev_installs,
        args.f,
    )

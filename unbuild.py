"""pkg-unbuild command to remove built package."""


import os
import shutil

from pkg import constants, utils


def add_subparser_command(subparser):
    """Add pkg-install subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    unbuild_command = subparser.add_parser(
        constants.UNBUILD,
        help="remove a built package",
    )

    unbuild_command.add_argument(
        "pkg_name",
        type=str,
        help="name of package to unbuild",
    )
    unbuild_command.add_argument(
        "version",
        type=str,
        help="version of package to unbuild",
    )
    unbuild_command.add_argument(
        "-f",
        action="store_true",
        help="force unbuild (don't ask for confirmation)",
    )
    unbuild_command.add_argument(
        "-d",
        action="store_true",
        help="unbuild from develop mode",
    )


def main(args):
    """Unbuild package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    if args.d:
        pkgs_dir = constants.DEV_PKGS_DIR
        pkg_builds_dir = constants.DEV_PKG_BUILDS_DIR
        success_message = "Dev Package Unbuilt Successfully"
    else:
        pkgs_dir = constants.PKGS_DIR
        pkg_builds_dir = constants.PKG_BUILDS_DIR
        success_message = "Package Unbuilt Successfully"

    pkg_builds_path = os.path.join(pkg_builds_dir, args.pkg_name)
    pkg_version_dir = os.path.join(pkg_builds_path, args.version)
    pkg_info_file = utils.get_package_info_file(pkg_version_dir)
    if not os.path.isfile(pkg_info_file):
        utils.print_error(
            "The given package {0} has no version {1} built under {2}",
            args.pkg_name,
            args.version,
            pkg_builds_path,
        )
        return

    installed_pkg_path = os.path.join(pkgs_dir, args.pkg_name)
    _, installed_pkg_info = utils.get_package_info(
        installed_pkg_path,
        print_on_error=False,
    )
    if installed_pkg_info:
        installed_version = installed_pkg_info.get(constants.VERSION_KEY)
        if installed_version == args.version:
            utils.print_error(
                "Cannot unbuild the version {0} build for package {1} "
                "as this version is currently installed. Run a pkg "
                "uninstall first".format(
                    args.version,
                    args.pkg_name,
                )
            )
            return

    continue_unbuild = args.f or utils.prompt_user_confirmation(
        "{0} package with version {1} found in {2}.\nContinue uninstall? "
        "[Y|n]".format(
            args.pkg_name,
            args.version,
            pkg_builds_path,
        ),
        confirmation_chars=['y', ''],
        accepted_chars=['y', 'n', ''],
    )
    if not continue_unbuild:
        print ("Aborting.")
        return

    shutil.rmtree(pkg_version_dir)
    print (success_message)

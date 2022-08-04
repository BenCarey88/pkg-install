"""pkg-uninstall command."""

import os
import shutil

from pkg import constants, utils


def add_subparser_command(subparser):
    """Add pkg-install subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    uninstall_command = subparser.add_parser(
        constants.UNINSTALL,
        help="uninstall a package",
    )

    uninstall_command.add_argument(
        "pkg_name",
        type=str,
        help="name of package to uninstall",
    )
    uninstall_command.add_argument(
        "-f",
        action="store_true",
        help="force uninstall (don't ask for confirmation)",
    )
    uninstall_command.add_argument(
        "-d",
        action="store_true",
        help="uninstall from develop mode",
    )


def main(args):
    """Uninstall package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    if args.d:
        pkgs_dir = constants.DEV_PKGS_DIR
        success_message = "Dev Package Uninstalled Successfully"
    else:
        pkgs_dir = constants.PKGS_DIR
        success_message = "Package Uninstalled Successfully"

    pkg_path = os.path.join(pkgs_dir, args.pkg_name)
    pkg_info_file = utils.get_package_info_file(pkg_path)

    if not os.path.isfile(pkg_info_file):
        utils.print_error(
            "The given package {0} is not currently installed in {1}",
            args.pkg_name,
            pkgs_dir,
        )
        return

    continue_uninstall = args.f or utils.prompt_user_confirmation(
        "{0} package found in {1}.\nContinue uninstall? [Y|n]".format(
            args.pkg_name,
            pkgs_dir,
        ),
        confirmation_chars=['y', ''],
        accepted_chars=['y', 'n', ''],
    )
    if not continue_uninstall:
        print ("Aborting.")
        return

    shutil.rmtree(pkg_path)
    print (success_message)

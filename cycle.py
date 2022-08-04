"""pkg-cycle command."""

import os

from pkg import build, constants, install, utils


def add_subparser_command(subparser):
    """Add pkg-cycle subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    cycle_command = subparser.add_parser(
        constants.CYCLE,
        help="build a package",
    )

    cycle_command.add_argument(
        "version",
        nargs="?",
        type=str,
        default="",
        help="Version for package build. If not given, use pkg-info",
    )
    cycle_command.add_argument(
        "-f",
        action="store_true",
        help="force install (don't ask for confirmation if overwriting)",
    )
    cycle_command.add_argument(
        "-d",
        action="store_true",
        help="install to develop mode",
    )


def main(args):
    """Build package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    if not args.d:
        keep_going = utils.prompt_user_confirmation(
            "[WARNING]: using pkg cycle outside of develop mode. "
            "Please ensure you are not overwriting a version. "
            "Would you like to continue? [y|N]",
            confirmation_chars=['y'],
            accepted_chars=['y', 'n', '']
        )
        if not keep_going:
            print ("Aborting.")
            return

    src_dir = os.path.abspath(os.getcwd())
    pkg_info_file, pkg_info = utils.get_package_info(src_dir)
    if not pkg_info:
        return

    pkg_name = pkg_info.get(constants.NAME_KEY)
    if not pkg_name:
        utils.print_error(
            "The pkg-info file has no pkg name:\n\n\t{0}",
            pkg_info_file,
        )
        return

    version = args.version or build.get_build_version(
        pkg_info,
        pkg_info_file,
        args.d
    )
    if not version:
        return

    build_success = build.run_build(version, args.d, args.f)
    if build_success:
        install.run_install(pkg_name, version, args.d, args.d, args.f)
    else:
        utils.print_error("Build failed - aborting.")

"""pkg-install command."""

from datetime import datetime
import json
import os
import shutil
import yaml

from pkg import constants, utils


def add_subparser_command(subparser):
    """Add pkg-build subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    build_command = subparser.add_parser(
        constants.BUILD,
        help="build a package",
    )

    build_command.add_argument(
        "version",
        nargs="?",
        type=str,
        default="",
        help="Version for package build. If not given, use pkg-info",
    )
    build_command.add_argument(
        "-f",
        action="store_true",
        help="force install (don't ask for confirmation if overwriting)",
    )
    build_command.add_argument(
        "-d",
        action="store_true",
        help="install to develop mode",
    )


def main(args):
    """Build package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    if args.d:
        build_dir = constants.DEV_PKG_BUILDS_DIR
        success_message = "Dev Package Built Successfully"
    else:
        build_dir = constants.PKG_BUILDS_DIR
        success_message = "Package Built Successfully"
    
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

    if args.version:
        version = args.version
    elif args.d:
        version = constants.DEFAULT_DEV_VERSION
        print ("Building version dev-0.0.0 (default dev version)")
    else:
        version = pkg_info.get(constants.VERSION_KEY)
        print (
            "Building version {0} (specified in pkg-info file)".format(version)
        )
    if not version:
        utils.print_error(
            "No version given and pkg-info file has no version set:\n\n\t{0}",
            pkg_info_file,
        )
        return

    if not args.d:
        if version != pkg_info.get(constants.VERSION_KEY):
            overwrite_version = utils.prompt_user_confirmation(
                "Version given ({0}) doesn't match version in pkg-info ({1}) "
                "Would you like to overwrite the pkg-info? [y|n]".format(
                    version,
                    pkg_info.get(constants.VERSION_KEY)
                ),
                confirmation_chars=['y',],
                accepted_chars=['y', 'n'],
            )
            if overwrite_version:
                pkg_info[constants.VERSION_KEY] = version
                with open(pkg_info_file, "w") as file_:
                    json.dump(pkg_info, file_, indent=4)

        version_info_file, version_info = utils.get_version_info(src_dir)
        if not version_info or not version_info.get(version):
            continue_build = utils.prompt_user_confirmation(
                "No info specified for version {0} in version info file"
                "\n\n\t{1}\n\nContinue anyway? [y|N]".format(
                    version,
                    version_info_file
                ),
                confirmation_chars=['y'],
                accepted_chars=['y', 'n', ''],
            )
            if not continue_build:
                print ("Aborting.")
                return

    pkg_build_dir = os.path.join(build_dir, pkg_name)
    if not os.path.isdir(pkg_build_dir):
        os.mkdir(pkg_build_dir)
    dest_dir = os.path.join(pkg_build_dir, version)
    success = utils.copy_package_directory(
        src_dir,
        dest_dir,
        pkg_name,
        pkg_info.get(constants.IGNORE_PATTERNS_KEY, []),
        args.d,
        args.f,
    )
    if not success:
        return

    dest_pkg_info = utils.get_package_info_file(dest_dir)
    pkg_info[constants.BUILD_TIME_KEY] = str(datetime.now().replace(microsecond=0))
    pkg_info[constants.VERSION_KEY] = version
    with open(dest_pkg_info, "w") as file_:
        json.dump(pkg_info, file_, indent=4)

    print (success_message)

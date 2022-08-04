"""pkg-build command."""

from datetime import datetime
import json
import os

from pkg import build, constants, install, utils


def add_subparser_command(subparser):
    """Add pkg-build subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    build_command = subparser.add_parser(
        constants.BUILD,
        help="build and install a package",
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


def get_build_version(pkg_info, pkg_info_file, dev_mode):
    """Get version to build, if none specified on commandline.

    Args:
        pkg_info (dict): pkg-info dictionary.
        pkg_info_file (str): path to pkg-info file.
        dev_mode (bool): whether or not we're building to dev builds directory.

    Returns:
        (str or None): version to build, if found.
    """
    if dev_mode:
        version = constants.DEFAULT_DEV_VERSION
        print ("Building version dev-0.0.0 (default dev version)")
    else:
        version = pkg_info.get(constants.VERSION_KEY)
        if not version:
            utils.print_error(
                "No version given and pkg-info file has no version:\n\n\t{0}",
                pkg_info_file,
            )
            return None
        print (
            "Building version {0} (specified in pkg-info file)".format(version)
        )
    return version


def run_build(version, dev_mode, force):
    """Run build action.

    Args:
        version (str or None): version to build. If None, use pkg-info.
        dev_mode (bool): whether or not to build in dev-builds directory.
        force (bool): if True, don't ask for confirmation when rewriting.

    Returns:
        (bool): if build was successful.
    """
    if dev_mode:
        build_dir = constants.DEV_PKG_BUILDS_DIR
        success_message = "Dev Package Built Successfully"
    else:
        build_dir = constants.PKG_BUILDS_DIR
        success_message = "Package Built Successfully"
    
    src_dir = os.path.abspath(os.getcwd())
    pkg_info_file, pkg_info = utils.get_package_info(src_dir)
    if not pkg_info:
        return False

    pkg_name = pkg_info.get(constants.NAME_KEY)
    if not pkg_name:
        utils.print_error(
            "The pkg-info file has no pkg name:\n\n\t{0}",
            pkg_info_file,
        )
        return False

    version = version or get_build_version(pkg_info, pkg_info_file, dev_mode)
    if not version:
        return False

    if not dev_mode:
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
                return False

    pkg_build_dir = os.path.join(build_dir, pkg_name)
    if not os.path.isdir(pkg_build_dir):
        os.mkdir(pkg_build_dir)
    dest_dir = os.path.join(pkg_build_dir, version)
    success = utils.copy_package_directory(
        src_dir,
        dest_dir,
        pkg_name,
        pkg_info.get(constants.IGNORE_PATTERNS_KEY, []),
        dev_mode,
        force,
    )
    if not success:
        return False

    dest_pkg_info = utils.get_package_info_file(dest_dir)
    pkg_info[constants.BUILD_TIME_KEY] = str(datetime.now().replace(microsecond=0))
    pkg_info[constants.VERSION_KEY] = version
    with open(dest_pkg_info, "w") as file_:
        json.dump(pkg_info, file_, indent=4)

    print (success_message)
    return True


def main(args):
    """Build and install package based on commandline args.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    run_build(args.version, args.d, args.f)

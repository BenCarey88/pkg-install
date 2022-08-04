"""pkg-query command for querying info."""

import os

from pkg import constants, utils


def add_subparser_command(subparser):
    """Add pkg-install subarser commands.

    Args:
        subparser (argparse.Parser): argparse object.
    """
    query_command = subparser.add_parser(
        constants.QUERY,
        help="list packages",
    )
    query_command.add_argument(
        "pkg_name",
        type=str,
        help="Package name to query",
    )
    query_command.add_argument(
        "-v",
        action="store_true",
        help="Query version of develop installs",
    )
    query_command.add_argument(
        "-d",
        action="store_true",
        help="Restrict query to develop installs",
    )


def main(args):
    """Query info for packages.

    Args:
        args (argparse.Namespace): arguments from commandline.
    """
    query_flags = [args.v]
    queried_flags = [flag for flag in query_flags if flag]
    if len(queried_flags) != 1:
        utils.print_error(
            "Query command must use exactly one of the following query "
            "flags: -v"
        )
    pkgs_dir = constants.DEV_PKGS_DIR if args.d else constants.PKGS_DIR
    pkg_dir = os.path.join(pkgs_dir, args.pkg_name)
    _, pkg_info = utils.get_package_info(pkg_dir)
    if args.v:
        print (pkg_info.get(constants.VERSION_KEY))

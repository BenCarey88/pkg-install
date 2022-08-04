import argparse

from pkg import (
    build,
    constants,
    cycle,
    install,
    list,
    query,
    unbuild,
    uninstall,
    utils,
)


def get_args():
    """Get args from argument parser.

    Returns:
        (argparse.Namespace): commandline arguments.
    """
    parser = argparse.ArgumentParser(
        description='Package development'
    )
    command = parser.add_subparsers(dest='command')
    build.add_subparser_command(command)
    cycle.add_subparser_command(command)
    install.add_subparser_command(command)
    list.add_subparser_command(command)
    query.add_subparser_command(command)
    unbuild.add_subparser_command(command)
    uninstall.add_subparser_command(command)
    return parser.parse_args()


def main():
    """Install package based on commandline args."""
    args = get_args()
    if args.command == constants.BUILD:
        build.main(args)
    elif args.command == constants.CYCLE:
        cycle.main(args)
    elif args.command == constants.INSTALL:
        install.main(args)
    elif args.command == constants.LIST:
        list.main(args)
    elif args.command == constants.QUERY:
        query.main(args)
    elif args.command == constants.UNBUILD:
        unbuild.main(args)
    elif args.command == constants.UNINSTALL:
        uninstall.main(args)
    elif args.command == "":
        utils.print_error("No subcommand given to 'pkg' command")
    else:
        utils.print_error("pkg subcommand {0} not recognised", args.command)


if __name__ == "__main__":
    main()

import argparse
import json
import os
import six
import shutil


def get_args():
    """Get args from argument parser.

    Returns:
        (argparse.Namespace): namespace for commandline args.
    """
    parser = argparse.ArgumentParser(
        description='Install packages to my package directory'
    )
    parser.add_argument(
        "src_dir",
        nargs="?",
        type=str,
        default=os.getcwd(),
        help="source directory for package",
    )
    parser.add_argument(
        "-s",
        action="store_true",
        help="whether or not to install as a script or as a package",
    )
    args = parser.parse_args()
    return args


def prompt_user_confirmation(
        message,
        confirmation_chars=['y', ''],
        accepted_chars=['y','n', '']):
    """Prompt user confirmation.

    Args:
        message (str): message to give user.
        confirmation_char (list(str)): characters that signal confirmation.
        accepted_chars (list(str)): characters required before user can continue.

    Returns:
        (bool): whether or not user has confirmed.
    """
    answer = None
    while answer not in accepted_chars:
        # six.moves.input is called input in python3, raw_input in python2
        answer = six.moves.input(message).lower()
    return answer in confirmation_chars


def main():
    """Install package based on commandline args."""
    args = get_args()
    src_dir = args.src_dir
    pkgs_dir = os.path.join(os.sep, "PythonPath", "my-pkgs")

    print (args.s)

    pkg_info_file = os.path.join(src_dir, "pkg-info.json")
    if not os.path.isfile(pkg_info_file):
        print (
            "[ERROR] The given directory\n\n\t{0}\n\n"
            "is not a package (it has no pkg-info.json file)\n".format(src_dir)
        )
        return

    with open(pkg_info_file) as file_:
        pkg_info = json.load(file_)

    pkg_name = pkg_info.get("name")
    if not pkg_name:
        print (
            "[ERROR] The pkg-info file has no pkg_name:\n\n\t{0}".format(
                pkg_info_file
            )
        )
        return
    
    dest_dir = os.path.join(pkgs_dir, pkg_name)
    if os.path.isdir(dest_dir):
        continue_install = prompt_user_confirmation(
            "{0} package already exists. Overwrite? [Y|n]".format(pkg_name),
            confirmation_chars=['y', ''],
            accepted_chars=['y', 'n', ''],
        )
        if not continue_install:
            print ("Aborting.")
            return
        else:
            shutil.rmtree(dest_dir)

    shutil.copytree(
        src_dir,
        dest_dir,
        ignore=shutil.ignore_patterns(
            "*.pyc",
            ".git*",
            "__pycache__"
        )
    )

    print ("Package installed successfully")


if __name__ == "__main__":
    main()

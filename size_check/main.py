import subprocess
import sys
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="Check the size of files being committed")
    parser.add_argument(
        "-sl",
        "--soft-limit",
        type=int,
        default=10000000,
        help="Soft size limit in bytes. Default is 10MB.",
    )
    parser.add_argument(
        "-hl",
        "--hard-limit",
        type=int,
        default=50000000,
        help="Hard size limit in bytes. Default is 50MB.",
    )
    args = parser.parse_args()

    status = 0

    def bytes_to_human(size):
        size = int(size)
        suffixes = ["B", "KB", "MB", "GB", "TB"]  # bigger suffixes are not needed
        i = 0
        while size > 1000 and i < len(suffixes) - 1:
            size /= 1000.0
            i += 1
        return "{:.1f}{}".format(size, suffixes[i])

    staged_files = subprocess.run(
        ["git", "diff", "-z", "--staged", "--name-only", "--diff-filter=d"],
        capture_output=True,
    ).stdout
    for file in staged_files.decode().split("\0"):
        if file:
            hash = subprocess.run(
                ["git", "ls-files", "-s", file], capture_output=True
            ).stdout.split()[1]
            size = int(
                subprocess.run(
                    ["git", "cat-file", "-s", hash], capture_output=True
                ).stdout
            )

            if size > args.hard_limit:
                print(
                    f"Error: Cannot commit '{file}' because it is {bytes_to_human(size)}, which exceeds the hard size limit of {bytes_to_human(args.hard_limit)}."
                )
                status = 1
            elif size > args.soft_limit:
                print(
                    f"Warning: '{file}' is {bytes_to_human(size)}, which exceeds the soft size limit of {bytes_to_human(args.soft_limit)}. Please double check that you intended to commit this file."
                )

    sys.exit(status)

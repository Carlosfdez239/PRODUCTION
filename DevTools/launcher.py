#!/usr/bin/env python3

import concurrent.futures
import json
import os
import subprocess
from typing import Dict, List

CONFIG_FILE: str = "gui_config.json"
MAX_CONCURRENT_THREADS: int = 5

# ANSI escape codes for text colors
RESET: str = "\033[0m"  # Reset color back to default
COLORS: Dict[str, str] = {
    "RED": "\033[31m",
    "GREEN": "\033[92m",
    "BLUE": "\033[34m",
    "BRAND_BLUE": "\033[38;5;33m",
    "LIGHT_BLUE": "\033[38;5;117m",
    "YELLOW": "\033[33m",
}


def get_script_directory() -> str:
    """
    Get the directory of where this python file is stored on the machine."

    Returns:
        str: The absolute directory of the current file
    """

    return os.path.dirname(os.path.abspath(__file__))


def run_devtool(name: str, args: List[str]) -> None:
    """
    Run a development tool with the specified name and arguments.

    Args:
        name (str): The name of the development tool.
        args (list): List of command-line arguments to pass to the tool.
    """
    script_dir = get_script_directory()
    os.chdir(os.path.join(script_dir, "InMsgs"))
    file_path = os.path.join(script_dir, "InMsgs", name)

    python_bin = os.path.join(script_dir, "venv/bin/python")
    command = f"{python_bin} {file_path} {' '.join(args)}"

    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return_code = process.wait()
        stdout, stderr = process.communicate()
        if stdout:
            print(f"\n{stdout}")
        if return_code != 0:
            if stderr:
                print(f"\n{COLORS['RED']}{stderr}{RESET}")

            print(f"Process exited with return code {return_code}")

    except Exception as e:
        print(f"An error occurred: {e}")


def load_config(filename: str) -> Dict:
    """
    Load configuration data from a JSON file.

    Args:
        filename (str): The name of the JSON file to load.

    Returns:
        dict: The loaded configuration data as a dictionary.
    """
    with open(filename, "r") as config_file:
        return json.load(config_file)


def get_options(config_data: Dict) -> List[Dict]:
    """
    Extract and format options from configuration data.

    Args:
        config_data (dict): Configuration data loaded from a JSON file.

    Returns:
        list: A list of dictionaries representing available options.
    """
    options = []
    for key, tool_list in config_data.items():
        for tool_name in tool_list:
            new_tool = {"name": tool_name, "args": []}
            options.append(new_tool)

    return options


def print_menu(options: List[Dict], num_columns: int = 2) -> None:
    """
    Print a menu of available options.

    Args:
        options (list): A list of dictionaries representing available options.
    """
    max_len = max(len(option.get("name").strip(".py")) for option in options)
    items_per_column = len(options) // num_columns + 1

    for i in range(items_per_column):
        for j in range(i, len(options), items_per_column):
            name = options[j].get("name").strip(".py")
            padding = " " * (max_len - len(name))
            print(
                f"\t{COLORS['YELLOW']}{j + 1}{RESET}. {name}{padding}",
                end="\t" if j + 1 < items_per_column else "\n",
            )

    # Print a newline if the last line didn't end with a newline
    if (len(options) % num_columns) != 0:
        print()


def main() -> None:
    config_data: Dict = load_config(CONFIG_FILE)
    options: List[Dict] = get_options(config_data)

    # Create a thread pool executor
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_THREADS) as executor:
        while True:
            print(f"What {COLORS['BLUE']}DevTool GUI{RESET} do you want to open?")
            print_menu(options, num_columns=2)

            choice: str = input(
                f"Choose an option ({COLORS['YELLOW']}1-{len(options)}{RESET}"
                f" or q to {COLORS['RED']}quit{RESET}): "
            ).lower()

            if choice == "q":
                break
            elif choice.isdigit():
                if 1 <= int(choice) <= len(options):
                    tool = options[int(choice) - 1]
                    name = tool.get("name")

                    print(f"Opened {COLORS['BLUE']}{name}{RESET}")
                    # Submit the run_devtool function to the thread pool
                    executor.submit(run_devtool, name, tool["args"])

                    input(f"Press any key to continue")
                else:
                    print("Invalid input. Please enter a valid number.")
            else:
                print("Invalid input. Please enter a valid number.")


if __name__ == "__main__":
    main()

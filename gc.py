import os
import stat
import datetime
from tabulate import tabulate
import subprocess
from humanize import naturalsize
import argparse
import re

parser = argparse.ArgumentParser(description='Sort files/directories based on different criteria.')
parser.add_argument('-s', '--sort-by', choices=['date', 'name', 'size'], default='name',
                    help='Specify how the output should be sorted: date, name, or size.')
args = parser.parse_args()

# Get the value of the "--sort-by" argument
sort_by = args.sort_by

# ANSI escape codes for colors
YELLOW = "\033[33m"
YELLOW_BOLD = "\033[1;33m"
BLUE = "\033[34m"
RED = "\033[31m"
RED_BOLD = "\033[1;31m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
BOLD_WHITE = "\033[1;37m"
GREEN = "\033[32m"
ORANGE = "\033[33m"
GRAY = "\033[90m"

# Create an empty list to store table rows
table = []

# Create a dictionary to store the original strings without ANSI escape codes
plain_strings_dict = {}

# Loop through files and directories in the current working directory
for i, item in enumerate(os.listdir('.')):
    path = os.path.join('.', item)
    if not os.path.exists(path):
        continue

    # Get file or subdirectory name
    name = item

    # Get file permissions
    permissions = stat.filemode(os.lstat(path).st_mode)

    # Get file size
    if os.path.isdir(path):
        # Get occupied disk space for directories using the `du` command
        size = subprocess.check_output(['du', '-sh', path]).decode().split('\t')[0]
        size = size.split()[0]  # Extract the size value
    else:
        # Get file size for other file types and humanize it
        size = os.path.getsize(path)
        size = naturalsize(size)

    # Get last modified date
    last_modified = os.path.getmtime(path)
    last_modified = datetime.datetime.fromtimestamp(last_modified)

    # Calculate time elapsed since last modification
    time_elapsed = datetime.datetime.now() - last_modified

    # Store the original name and last_modified value along with ANSI escape codes
    original_name = name
    original_last_modified = last_modified.strftime('%Y-%m-%d %H:%M')
    name_ansi = name#f"{RESET}{name}{RESET}"
    last_modified_ansi = f"{RESET}{last_modified:%Y-%m-%d %H:%M}{RESET}"

    # Apply color based on file type
    if os.path.isdir(path):
        name_ansi = f"{YELLOW_BOLD}{name_ansi}{RESET}"
    elif original_name.endswith('.py'):
        name_ansi = f"{BLUE}{name_ansi}{RESET}"
    elif original_name.endswith('.log'):
        name_ansi = f"{YELLOW}{name_ansi}{RESET}"
    elif original_name.endswith('.f90') or original_name.endswith('.f95'):
        name_ansi = f"{RED}{name_ansi}{RESET}"
    elif original_name.endswith('.c') or original_name.endswith('.cpp'):
        name_ansi = f"{YELLOW}{name_ansi}{RESET}"
    else:
        name_ansi = f"{RESET}{name_ansi}{RESET}"
        
    # Apply color based on file size
    if size.endswith("Bytes") or size.endswith("kB"):
        size = f"{GREEN}{size}{RESET}"
    elif size.endswith("MB") or size.endswith("M"):
        size = f"{YELLOW}{size}{RESET}"
    elif size.endswith("GB") or size.endswith("TB"):
        size = f"{RED}{size}{RESET}"
    else:
        size = f"{ORANGE}{size}{RESET}"

    # Apply color based on time elapsed since last modification
    if time_elapsed.days > 365:
        last_modified_ansi = f"{GRAY}{original_last_modified}{RESET}"
    elif time_elapsed.days > 180:
        last_modified_ansi = f"{original_last_modified}"
    elif time_elapsed.days > 7:
        last_modified_ansi = f"{MAGENTA}{original_last_modified}{RESET}"
    elif time_elapsed.total_seconds() < 86400:
        last_modified_ansi = f"{GREEN}{original_last_modified}{RESET}"
    else:
        last_modified_ansi = f"{BLUE}{original_last_modified}{RESET}"
    
    # Append the row to the table with background color applied
    table.append([permissions, size, last_modified_ansi, name_ansi])

    # Save the original values without ANSI escape codes for later restoration
    plain_strings_dict[(original_name, original_last_modified)] = (name_ansi, last_modified_ansi)
    

# Sort the table based on the sort_by argument
if sort_by == 'date':
    table.sort(key=lambda row: datetime.datetime.strptime(re.sub(r'\x1b\[.*?m', '', row[2]), '%Y-%m-%d %H:%M'))
elif sort_by == "name":
    table.sort(key=lambda row: re.sub(r'\x1b\[.*?m', '', row[3]))

# Restore the original names and last modified values
for i, row in enumerate(table):
    name, last_modified = row[3], row[2]
    table[i][3], table[i][2] = plain_strings_dict[(re.sub(r'\x1b\[.*?m', '', name), re.sub(r'\x1b\[.*?m', '', last_modified))]

# Format the headers with ANSI escape code for bold
headers = [f"{BOLD_WHITE}{header}{RESET}" for header in ['Permissions', 'Disk Space', 'Last Modified', 'Name']]

# Create the separating line
separator = ['----'] * len(headers)

# Combine the headers, separator, and table rows
nthingies = 10
output = [headers, separator] + table

# Print the table with custom table style
print(tabulate(output, tablefmt='plain', numalign='left'))

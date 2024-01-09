import os

# Function to extract file number from a line
def extract_file_number(line):
    if line.startswith("//file"):
        return int(line[6:])
    return None

# Function to read files, extract content, and append to a single file
def rename_files():
    file_list = [filename for filename in os.listdir() if filename.endswith(".pcap")]

    for file_path in file_list:
        with open(file_path, "r") as file:
            for line in file:
                n = extract_file_number(line.strip())


rename_files()

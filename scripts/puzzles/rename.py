import os

def extract_file_number(line):
    if line.startswith("//file"):
        return int(line[6:])
    return None

def rename_files():
    file_list = [filename for filename in os.listdir() if filename.endswith(".pcap")]

    for file_path in file_list:
        with open(file_path, "r") as file:
            for line in file:
                n = extract_file_number(line.strip())

def merge_files():
    file_list = [filename for filename in os.listdir() if filename.endswith(".txt")]
    file_list.sort(key=lambda x: int(x.split(".txt")[0]))
    with open("file.c", "w") as merged_file:
        for file_path in file_list:
            with open(file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip(f"//file{file_path}")
                    merged_file.write(line)

rename_files()
merge_files()
import os

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

merge_files()

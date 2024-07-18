import os
import glob

def get_latest_file_in_folder(folderpath, postfix:str="", extension:str="csv"):
    list_of_files = glob.glob(f"{folderpath}*{postfix}.{extension}") # * means all if need specific format then *.csv
    if len(list_of_files) > 0:
        return max(list_of_files, key=os.path.getctime)
    else:
        return None

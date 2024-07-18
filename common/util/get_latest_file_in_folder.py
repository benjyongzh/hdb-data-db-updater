import os
import glob

def get_latest_file_in_folder(folderpath):
    list_of_files = glob.glob(folderpath + '*.csv') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file
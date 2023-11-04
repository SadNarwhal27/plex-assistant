import os

def change_file_name(folder_path, text_to_add):
    file_list = os.listdir(folder_path)

    files_changed = 0
    for filename in file_list:
        if os.path.isfile(os.path.join(folder_path, filename)):
            new_filename = text_to_add + filename
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
            files_changed += 1
    print(f'\nTotal Files Changed: {files_changed}')
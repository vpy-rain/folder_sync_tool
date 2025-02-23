import shutil
import os
import argparse
import time
import schedule
import re
import logging

class FolderCopy: 
    #Class defining folder operations necessary to perform task and relate settings
    def __init__(self, source_folder_path, target_folder_path, replication_time):
        self.source_folder_path: str = source_folder_path
        self.target_folder_path: str = target_folder_path
        self.replication_time: str = replication_time

    def get_path_details(self, path):
        # Check path for files and folders 
        path_files_abs, path_dirs_abs = [], []
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    path_files_abs.append(os.path.join(root, file))
                for dir in dirs:
                    path_dirs_abs.append(os.path.join(root, dir))
        except FileNotFoundError as e:
            logger.info(f"The folder path {path} does not exist., {e}")
        except Exception as e:
            logger.info(f"An error occurred {e}.")
        return path_files_abs, path_dirs_abs
    
    def compare_dirs(self, loc_dirs, dest_dirs):
        #Compare folders in source and destination
        src_dirpaths_rel = [os.path.relpath(dirpath, self.source_folder_path) for dirpath in loc_dirs]
        dest_dirpaths_rel = [os.path.relpath(dirpath, self.target_folder_path) for dirpath in dest_dirs]
        dirs_to_add = [dir for dir in src_dirpaths_rel if dir not in dest_dirpaths_rel]
        dirs_to_remove = [dir for dir in dest_dirpaths_rel if dir not in src_dirpaths_rel]
        return dirs_to_add, dirs_to_remove

    def compare_files(self, location_files, destination_files):
        #Compare files in source and destination
        files_to_add, files_to_remove, files_to_update = [], [], []
        source_filepaths_rel = [os.path.relpath(location_file, self.source_folder_path) for location_file in location_files]
        dest_filepaths_rel = [os.path.relpath(destination_file, self.target_folder_path) for destination_file in destination_files]
        files_to_add = [file for file in source_filepaths_rel if file not in dest_filepaths_rel]
        files_to_remove = [file for file in dest_filepaths_rel if file not in source_filepaths_rel]
        common_files = [file for file in source_filepaths_rel if file in dest_filepaths_rel]
        files_to_update = [
            file for file in common_files
            if os.path.getmtime(os.path.join(self.source_folder_path, file))
            != os.path.getmtime(os.path.join(self.target_folder_path, file))
            ]
        return files_to_add, files_to_remove, files_to_update                                      

    def dir_copy(self, dirs_to_copy):
        #Copy folders
        logger.info(f'Created {len(dirs_to_copy)} folders: {dirs_to_copy}')
        for dir in dirs_to_copy:
            os.makedirs(os.path.join(self.target_folder_path, dir), exist_ok=True)

    def dir_remove(self, dirs_to_remove):
        #Remove folders
        logger.info(f'Deleted {len(dirs_to_remove)} folders: {dirs_to_remove}')   
        for dir in dirs_to_remove:
            shutil.rmtree(os.path.join(self.target_folder_path, dir))
    
    def copy(self, files_to_add):
        #Copy files from source to destination
        logger.info(f'Copied {len(files_to_add)} files: {files_to_add}')
        for rel_path in files_to_add:
            src_path = os.path.join(self.source_folder_path, rel_path)
            dest_path = os.path.join(self.target_folder_path, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)

    def remove(self, files_to_remove):
        #Remove files from destination which are not in source
        logger.info(f'Deleted {len(files_to_remove)} files: {files_to_remove}')
        for rel_path in files_to_remove:
            dest_path = os.path.join(self.target_folder_path, rel_path)
            os.remove(dest_path)

    def update(self, files_to_update):
        #Update files from source to destination
        logger.info(f'Updated {len(files_to_update)} files: {files_to_update}')
        for rel_path in files_to_update:
            src_path = os.path.join(self.source_folder_path, rel_path)
            dest_path = os.path.join(self.target_folder_path, rel_path)
            shutil.copy2(src_path, dest_path)

    def scheduler(self):
    #Setup periodic time for replica process
        def job():
            loc_files_details, loc_dirs_details = self.get_path_details(self.source_folder_path)
            dest_files_details, dest_dirs_details = self.get_path_details(self.target_folder_path)
            dir_added, dir_removed = self.compare_dirs(loc_dirs=loc_dirs_details, dest_dirs=dest_dirs_details)
            added, removed, updated  = self.compare_files(location_files=loc_files_details, destination_files=dest_files_details)
            self.remove(removed)
            self.dir_copy(dir_added)
            self.dir_remove(dir_removed)
            self.copy(added)
            self.update(updated)
        
        separated_scheduler = self.replication_time.split(" ")
        time_form = separated_scheduler[1]
        if time_form == "seconds":
            schedule.every(int(separated_scheduler[0])).seconds.do(job)
        elif time_form == "minutes":
            schedule.every(int(separated_scheduler[0])).minutes.do(job)
        elif time_form == "hours":
            schedule.every(int(separated_scheduler[0])).hours.do(job)
        elif time_form == "days":
            schedule.every(int(separated_scheduler[0])).days.do(job)
        elif time_form == "weeks":
            schedule.every(int(separated_scheduler[0])).weeks.do(job)
        else:
            raise ValueError(f"Unsuppored time form: {time_form}")

        job()
        logger.info(f"Initial copying and removal is complete. Next run will occur in {separated_scheduler[0]} {separated_scheduler[1]}.")

        while True:
            schedule.run_pending()
            time.sleep(1)

def regex_scheduler_validation(regex_value):
# Defines accepted values for the scheduler
    if not re.match(r"^\d{1,2} (seconds|minutes|hours|days|weeks)$", regex_value):
        raise argparse.ArgumentTypeError(f"Your answer - '{regex_value}' did not match the required format.")
    return regex_value


if __name__ == "__main__":
    #Processes the whole logic - parse input arguments, log them, and start subprocesses
    parser = argparse.ArgumentParser(description="obtain all the required inputs for processing - input file, output file, and schedule")
    parser.add_argument('--location_path', type=str, required=True)
    parser.add_argument('--destination_path', type=str, required=True)
    parser.add_argument('--replication_time', type=regex_scheduler_validation, required=True, help="Input the frequency of synchronization (Use the following format: 2 digits+space+seconds/minutes/hour/day/week)")
    parser.add_argument('--log_file_path', type=str, required=True, help='log file path')
    args = parser.parse_args()
    
    logging.basicConfig(
            filename=args.log_file_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    
    instance = FolderCopy(
        source_folder_path=args.location_path,
        target_folder_path=args.destination_path,
        replication_time=args.replication_time
    )
    instance.scheduler()
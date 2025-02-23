# Folder Synchronization Tool

This tool synchronizes files and directories from a source location to a destination location at specified intervals. It supports copying, removing, and updating files and directories based on the provided schedule.

## Features

- Copy files and directories from a source location to a destination location.
- Remove files and directories from the destination location.
- Schedule synchronization tasks at specified intervals (e.g., minutes, hours, days, weeks).
- Log synchronization activities to a specified log file.

## Requirements

- Python 3.x

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/vpy-rain/folder_sync_tool.git
    cd folder_sync_tool
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the `src/folder_sync_manager.py` script with the required arguments:

```sh
python src/folder_sync_manager.py --location_path <source_folder_path> --destination_path <destination_folder_path> --replication_time "<interval> <unit>" --log_file_path <log_file_path>
```

## Logging

The tool logs synchronization activities to the specified log file. The log format includes the timestamp, log level, and message. The following points are logged:

- Initialization of the synchronization process.
- Scheduling of tasks with the specified intervals.
- Copying of files and directories.
- Removal of files and directories.
- Checking for scheduled tasks.
- Any errors or exceptions that occur during the process.

### Example Log Entry

```sh
2023-10-01 12:00:00 - INFO - Copying files: ['file1.txt', 'file2.txt']
2023-10-01 12:00:00 - INFO - Removing files: ['file3.txt']
2023-10-01 12:02:00 - INFO - Checking for scheduled tasks...
```
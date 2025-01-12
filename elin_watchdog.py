import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re

# Directory to monitor
# Modify this to actual Save Folder Path!!!
watch_directory = '/Users/username/CXPBottles/Steam/drive_c/users/crossover/AppData/LocalLow/Lafrontier/Elin/Save'

class FolderHandler(FileSystemEventHandler):
    def __init__(self):
        self.current_observer = None  # Store the current observer

    def on_created(self, event):
        """Handle new folder creation events"""
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
            # Check if it's a world folder
            if re.match(r'^world_\d+$', folder_name):
                print(f"New world folder detected: {event.src_path}")
                # Switch to monitor this world folder
                self.monitor_world_folder(event.src_path)

    def monitor_world_folder(self, folder_path):
        """Monitor a specific world folder for '7' and 'Temp' folders"""
        print(f"Switching to monitor: {folder_path}")
        if self.current_observer:
            self.current_observer.stop()
            self.current_observer.join()

        # Start observing the new folder
        self.current_observer = Observer()
        event_handler = FileSystemEventHandler()
        event_handler.on_created = self.on_subfolder_created
        self.current_observer.schedule(event_handler, folder_path, recursive=True)
        self.current_observer.start()

        # Check existing folders immediately
        self.check_and_delete_temp(folder_path)

    def on_subfolder_created(self, event):
        """Handle creation of '7' or 'Temp' folders inside a world folder"""
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
            parent_folder = os.path.dirname(event.src_path)

            if folder_name == '7':
                print(f"Detected '7' folder in {parent_folder}, checking for 'Temp'...")
                self.delete_temp_if_exists(parent_folder)
            elif folder_name == 'Temp':
                print(f"Detected 'Temp' folder in {parent_folder}, checking for '7'...")
                self.delete_temp_if_exists(parent_folder)

    def check_and_delete_temp(self, folder_path):
        """Check for both '7' and 'Temp' folders, and delete 'Temp' if both exist"""
        temp_folder = os.path.join(folder_path, 'Temp')
        folder_7 = os.path.join(folder_path, '7')

        if os.path.exists(folder_7):
            print(f"Found '7' folder in {folder_path}")
            if os.path.exists(temp_folder):
                print(f"Found 'Temp' folder in {folder_path}, deleting...")
                shutil.rmtree(temp_folder)
                self.restart_monitoring()
        elif os.path.exists(temp_folder):
            print(f"'Temp' folder exists in {folder_path}, waiting for '7' folder...")

    def delete_temp_if_exists(self, folder_path):
        """Delete the 'Temp' folder if it exists alongside '7'"""
        temp_folder = os.path.join(folder_path, 'Temp')
        folder_7 = os.path.join(folder_path, '7')

        if os.path.exists(folder_7) and os.path.exists(temp_folder):
            print(f"Deleting 'Temp' folder in {folder_path}...")
            shutil.rmtree(temp_folder)
            self.restart_monitoring()

    def restart_monitoring(self):
        """Switch back to monitoring the Save folder"""
        print(f"Restoring to monitor: {watch_directory}")
        if self.current_observer:
            self.current_observer.stop()
            self.current_observer.join()

        self.current_observer = Observer()
        self.current_observer.schedule(self, watch_directory, recursive=True)
        self.current_observer.start()


# Start monitoring the Save folder
event_handler = FolderHandler()
observer = Observer()
observer.schedule(event_handler, watch_directory, recursive=True)
observer.start()

print(f"Started monitoring directory: {watch_directory}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print("Stopped monitoring.")
observer.join()

import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re

# Directory to monitor
# Put your save path here
# example: /Users/username/CXPBottles/Steam/drive_c/users/crossover/AppData/LocalLow/Lafrontier/Elin/Save
watch_directory = ''


class FolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if it's a directory creation event
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
            # Only handle folders that match the pattern world
            if re.match(r'^world_\d+$', folder_name):
                print(f"New world folder created: {event.src_path}")
                # Start monitoring the new world folder
                self.monitor_world_folder(event.src_path)

    def monitor_world_folder(self, folder_path):
        """Monitor the creation of '7' and 'Temp' folders inside the world folder"""
        print(f"Monitoring folders inside {folder_path}")

        # Start observing the folder
        observer = Observer()
        event_handler = FileSystemEventHandler()
        event_handler.on_created = self.on_subfolder_created
        observer.schedule(event_handler, folder_path, recursive=True)
        observer.start()

        # First, check if '7' and 'Temp' folders already exist
        self.check_and_delete_temp(folder_path)

        try:
            while True:
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            observer.stop()
            print(f"Stopped monitoring {folder_path}")
            # After stopping the observer, return to monitoring the main Save folder
            self.restart_monitoring()

        observer.join()

    def on_subfolder_created(self, event):
        """Check if a new subfolder is '7' or 'Temp', and perform actions accordingly"""
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
            parent_folder = os.path.dirname(event.src_path)

            if folder_name == '7':
                # If '7' folder is created, check and delete 'Temp' folder
                self.delete_temp_if_exists(parent_folder)
            elif folder_name == 'Temp':
                # If 'Temp' folder is created, check if '7' folder exists
                self.delete_temp_if_exists(parent_folder)
            else:
                # If the folder is neither '7' nor 'Temp', continue monitoring the parent folder
                print(f"Other folder {folder_name} created in {parent_folder}")

    def check_and_delete_temp(self, parent_folder):
        """Check if '7' and 'Temp' folders exist in the world folder, and delete Temp if both are present"""
        temp_folder = os.path.join(parent_folder, 'Temp')
        subfolder_7 = os.path.join(parent_folder, '7')

        if os.path.exists(subfolder_7) and os.path.isdir(subfolder_7):
            # If '7' folder exists, check if 'Temp' exists and delete it
            if os.path.exists(temp_folder) and os.path.isdir(temp_folder):
                print(f"Found both '7' and 'Temp' folders in {parent_folder}, deleting Temp folder")
                shutil.rmtree(temp_folder)
                # After deleting Temp, switch back to listening the main Save folder
                self.restart_monitoring()
        elif os.path.exists(temp_folder) and os.path.isdir(temp_folder):
            # If 'Temp' exists but no '7', continue monitoring this folder until '7' is created
            print(f"Found 'Temp' folder but no '7' folder in {parent_folder}, continuing to monitor...")
        else:
            # If neither folder exists, continue monitoring
            print(f"Neither '7' nor 'Temp' folder found in {parent_folder}, continuing to monitor...")

    def delete_temp_if_exists(self, parent_folder):
        """Check if a 'Temp' folder exists in parent_folder, and delete it if it does"""
        temp_folder = os.path.join(parent_folder, 'Temp')
        subfolder_7 = os.path.join(parent_folder, '7')

        # Check if 'Temp' folder exists and delete it
        if os.path.exists(temp_folder) and os.path.isdir(temp_folder):
            # If '7' folder exists, delete 'Temp'
            if os.path.exists(subfolder_7) and os.path.isdir(subfolder_7):
                print(f"Found both '7' and 'Temp' folders in {parent_folder}, deleting Temp folder")
                shutil.rmtree(temp_folder)
                # After deleting Temp, switch back to listening the main Save folder
                self.restart_monitoring()

    def restart_monitoring(self):
        """Restart monitoring the main Save folder after deletion or fallback"""
        print("Restarting monitoring of the Save directory...")
        observer.stop()  # Stop current monitoring
        observer.join()  # Wait for the observer to stop
        observer.schedule(event_handler, watch_directory, recursive=True)  # Re-schedule the Save folder
        observer.start()  # Restart observer


# Create event handler
event_handler = FolderHandler()
observer = Observer()
observer.schedule(event_handler, watch_directory, recursive=True)

# Start monitoring
observer.start()
print(f"Started monitoring directory: {watch_directory}")

# Keep the program running to continuously monitor
try:
    while True:
        time.sleep(1)  # Check every second
except KeyboardInterrupt:
    observer.stop()
    print("Stopped monitoring")
observer.join()

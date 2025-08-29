import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from pynput import keyboard
from collections import OrderedDict

import sys
import os
import random
import datetime
import argparse

snapshots = OrderedDict()
num_snapshots = 0
snapshot_labels = {}
snapshot_folder = "~/.snapshots"

def delete_excess_snapshot():
    global num_snapshots
    global snapshots

    if num_snapshots > 10:
        normal_snapshots = [x for x in snapshots.keys() if "sec" not in x]
        if len(normal_snapshots) == 0:
            return
        oldest_snap = normal_snapshots[0]
        oldest_file_name = snapshots[oldest_snap]
        del snapshots[oldest_snap]
        os.remove(oldest_file_name)
        clear_label(oldest_snap)
        num_snapshots -= 1

def clear_label(name):
    global snapshot_labels
    label = snapshot_labels[name]
    label.destroy()
    del snapshot_labels[name]
    
def snapshot_process():
    delete_excess_snapshot()

    take_snapshot(None, normal=True)
    display_snapshots()
    root.after(10000, snapshot_process)
    
def take_snapshot(e, normal=False):
    global snapshots
    global num_snapshots

    delete_excess_snapshot()
    
    content = text_pad.get("1.0", "end")

    now = datetime.datetime.now()

    f_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    if normal:
        file_name = f"snapshot_{f_time}.txt"
    else:
        file_name = f"sec_snapshot_{f_time}.txt"

    file_path = os.path.join(file_prefix_path, file_name)
    
    fd = open(file_path, 'w')
    fd.write(content)
    fd_rw.seek(0)
    fd_rw.write(content)
    fd.close()

    s_name = f"Snapshot at {f_time}"
    snapshots[s_name] = file_path
    num_snapshots += 1
    display_snapshots()
    
def display_snapshots():
    global snapshot_labels
    for i, snap in enumerate(list(snapshots.keys())):
        label = tk.Label(root, text=snap)
        label.grid(row=i, column=1, padx=10, pady=10, sticky="w")
        snapshot_labels[snap] = label
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, type=str, help="File name to save the snapshots")
    args = parser.parse_args()

    file_prefix = args.file

    if not os.path.isdir(os.path.expanduser(snapshot_folder)):
        os.mkdir(os.path.expanduser(snapshot_folder))

    file_prefix_path = os.path.join(os.path.expanduser(snapshot_folder), file_prefix)
    if not os.path.isdir(file_prefix_path):
        os.mkdir(file_prefix_path)

    try:
        fd_rw = open(file_prefix, "r+")
        content_init = fd_rw.read()
    except:
        print("File not found in current folder, opening empty file")
        pass
    
    root = tk.Tk()

    root.title("Snapshot Editor")
    root.bind_all('<Control-s>', take_snapshot)

    text_pad = ScrolledText(root, font=("Consolas", 25))
    text_pad.grid(row=0, column=0, rowspan=10, padx=10, pady=10, sticky="nsew")
    text_pad.delete("1.0", tk.END)

    text_pad.insert(tk.END, content_init)
    
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    for i in range(10):
        root.grid_rowconfigure(i, weight=1)

    root.after(10000, snapshot_process)
    root.mainloop()

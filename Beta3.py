# ---------------------------- Import Statements -----------------------------------------------------------------------------------------

import os
import asyncio
import aiohttp
import re
import string
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import multiprocessing
import queue
import time
from urllib.parse import urlparse, urlunparse
import json

# ---------------------------- Global Variables ------------------------------------------------------------------------------------------

# Global variable to store concurrency limit
concurrency_limit_value = multiprocessing.Value('i', 5000)

# Default character set
default_combo_set = string.ascii_letters + string.digits
current_combo_set = default_combo_set

# ---------------------------- Function Definitions --------------------------------------------------------------------------------------

def update_concurrency_limit(val):
    """Update the concurrency limit value."""
    with concurrency_limit_value.get_lock():
        concurrency_limit_value.value = int(val)

def increment_link_combo(combo, combo_set):
    """Increment the link combination string."""
    combo_list = list(combo)
    i = len(combo_list) - 1
    while i >= 0:
        current_index = combo_set.index(combo_list[i])
        if current_index == len(combo_set) - 1:
            combo_list[i] = combo_set[0]
            i -= 1
        else:
            combo_list[i] = combo_set[current_index + 1]
            break
    else:
        combo_list = [combo_set[0]] * (len(combo_list) + 1)
    return ''.join(combo_list)

async def fetch_url(session, url):
    """Asynchronously fetch the URL."""
    try:
        async with session.get(url, allow_redirects=False) as response:
            return response, await response.text()
    except Exception:
        return None, None

async def check_link(session, url, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, base_urls):
    """Check if the URL redirects to a valid SoundCloud link."""
    if stop_flag.value:
        return

    while pause_flag.value:
        await asyncio.sleep(0.1)

    response, text = await fetch_url(session, url)
    with total_requests.get_lock():
        total_requests.value += 1

    if response and response.status == 302:
        full_url = response.headers.get('Location', '')
        url_final = urlunparse(urlparse(full_url)._replace(query=''))
        match = re.search(r'/s-[a-zA-Z0-9]{11}', url_final)
        if match and (not base_urls or any(base_url in url_final for base_url in base_urls)):
            matched_urls_queue.put(url_final)
            with matched_urls_count.get_lock():
                matched_urls_count.value += 1

async def worker(process_id, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, combo_set, base_urls, active_tasks_count):
    """Async worker function for each process."""
    async with aiohttp.ClientSession() as session:
        tasks = set()
        while not stop_flag.value:
            with concurrency_limit_value.get_lock():
                concurrency_limit = concurrency_limit_value.value
            while len(tasks) < concurrency_limit and not stop_flag.value:
                with link_combo_lock:
                    current_combo = link_combo.value
                    link_combo.value = increment_link_combo(link_combo.value, combo_set)
                url = f"https://on.soundcloud.com/{current_combo}"
                task = asyncio.create_task(check_link(session, url, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, base_urls))
                tasks.add(task)
                task.add_done_callback(lambda t: tasks.discard(t))
                # Update active tasks count
                with active_tasks_count.get_lock():
                    active_tasks_count.value += 1
                task.add_done_callback(lambda t: decrement_active_tasks(active_tasks_count))
            await asyncio.sleep(0.1)

def decrement_active_tasks(active_tasks_count):
    """Decrement the active tasks count."""
    with active_tasks_count.get_lock():
        active_tasks_count.value -= 1

def process_worker(process_id, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, combo_set, base_urls, active_tasks_count):
    """Worker function for each process."""
    asyncio.run(worker(process_id, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, combo_set, base_urls, active_tasks_count))

def main(num_processes, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, combo_set, base_urls, active_tasks_count):
    """Main function to start processes."""
    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=process_worker, args=(i, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, combo_set, base_urls, active_tasks_count))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def saver_thread(stop_flag, matched_urls_queue, total_requests, links_per_minute):
    """Thread to save matched URLs to a file and calculate links per minute."""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{date_str}.txt"
    f = open(output_filename, "a")
    last_total_requests = total_requests.value
    last_time = time.time()
    try:
        while not stop_flag.value or not matched_urls_queue.empty():
            try:
                url = matched_urls_queue.get(timeout=1)
                f.write(url + '\n')
                f.flush()  # Ensure the URL is written to the file immediately
                os.fsync(f.fileno())  # Force write to disk
            except queue.Empty:
                pass
            current_time = time.time()
            if current_time - last_time >= 10:
                with total_requests.get_lock():
                    current_total_requests = total_requests.value
                delta_requests = current_total_requests - last_total_requests
                with links_per_minute.get_lock():
                    links_per_minute.value = delta_requests * 6  # 6 intervals of 10 seconds in a minute
                last_total_requests = current_total_requests
                last_time = current_time
    except Exception as e:
        print(f"Error in saver thread: {e}")
    finally:
        f.close()
        print(f"All URLs saved to {output_filename}")

def on_start(stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, base_urls, active_tasks_count):
    """Handle the Start button click event."""
    global last_update_time, last_total_requests, saver_thread_obj, num_processes, current_combo_set
    last_update_time = time.time()  # Initialize last update time
    last_total_requests = 0  # Initialize last total requests

    stop_flag.value = False
    pause_flag.value = False
    total_requests.value = 0
    matched_urls_count.value = 0
    active_tasks_count.value = 0

    link_combo.value = entry_starting_point.get()

    # Get character set from user input
    combo_set = entry_char_set.get()
    if not combo_set:
        messagebox.showerror("Error", "Character set cannot be empty.")
        return

    # Save combo_set to be used in update_status
    current_combo_set = combo_set

    try:
        num_processes = int(entry_num_processes.get())
    except ValueError:
        messagebox.showerror("Error", "Number of processes must be an integer.")
        return

    start_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)

    # Start the saver thread
    saver_thread_obj = threading.Thread(target=saver_thread, args=(stop_flag, matched_urls_queue, total_requests, links_per_minute))
    saver_thread_obj.daemon = True
    saver_thread_obj.start()

    # Start the main function in a separate thread
    threading.Thread(target=lambda: main(num_processes, stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, combo_set, base_urls, active_tasks_count), daemon=True).start()
    update_status_periodically(stop_flag, total_requests, matched_urls_count, link_combo, active_tasks_count, links_per_minute)

def on_stop(stop_flag):
    """Handle the Stop button click event."""
    global saver_thread_obj
    stop_flag.value = True
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, "Stopping in progress, please wait a moment...\n")
    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL)
    # Wait for the saver thread to finish
    saver_thread_obj.join()
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, "Stopped.\n")
    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)

def on_pause(pause_flag):
    """Handle the Pause/Resume button click event."""
    pause_flag.value = not pause_flag.value
    if pause_flag.value:
        status_text.config(state=tk.NORMAL)
        status_text.insert(tk.END, "Paused...\n")
        status_text.see(tk.END)
        status_text.config(state=tk.DISABLED)
        pause_button.config(text="Resume")
    else:
        status_text.config(state=tk.NORMAL)
        status_text.insert(tk.END, "Resuming...\n")
        status_text.see(tk.END)
        status_text.config(state=tk.DISABLED)
        pause_button.config(text="Pause")

def update_status(stop_flag, total_requests, matched_urls_count, link_combo, active_tasks_count, links_per_minute):
    """Update the status text in the GUI."""
    global last_update_time, last_total_requests, num_processes, current_combo_set

    status_text.config(state=tk.NORMAL)
    status_text.delete("1.0", tk.END)
    status_text.insert(tk.END, f"Links Checked Total: {total_requests.value}\n")
    status_text.insert(tk.END, f"Links Found: {matched_urls_count.value}\n")
    status_text.insert(tk.END, f"Links Checked per Minute: {links_per_minute.value}\n")
    status_text.insert(tk.END, f"Current Link Combo: {link_combo.value}\n")
    status_text.insert(tk.END, f"Processes (Threads): {num_processes}\n")
    with concurrency_limit_value.get_lock():
        concurrency_limit = concurrency_limit_value.value
    status_text.insert(tk.END, f"Concurrency per Process: {concurrency_limit}\n")
    total_tasks = num_processes * concurrency_limit
    status_text.insert(tk.END, f"Max Tasks On Machine: {total_tasks}\n")
    status_text.insert(tk.END, f"Active Tasks On Machine: {active_tasks_count.value}\n")
    status_text.insert(tk.END, f"Character Set: {current_combo_set}\n")

    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)

def update_status_periodically(stop_flag, total_requests, matched_urls_count, link_combo, active_tasks_count, links_per_minute):
    """Periodically update the status."""
    update_status(stop_flag, total_requests, matched_urls_count, link_combo, active_tasks_count, links_per_minute)
    if not stop_flag.value:
        root.after(1000, update_status_periodically, stop_flag, total_requests, matched_urls_count, link_combo, active_tasks_count, links_per_minute)

def select_artist_file(base_urls):
    """Handle the selection of the artist file."""
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        entry_artist_file.delete(0, tk.END)
        entry_artist_file.insert(0, file_path)
        try:
            with open(file_path, "r") as f:
                base_urls[:] = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Error reading base URLs file: {e}")
    else:
        base_urls[:] = []

def save_state():
    """Save the current state to a file."""
    state = {
        'link_combo': link_combo.value,
        'total_requests': total_requests.value,
        'matched_urls_count': matched_urls_count.value,
        'character_set': current_combo_set
    }
    with open('state.json', 'w') as f:
        json.dump(state, f)
    messagebox.showinfo("Save State", "Current state saved successfully.")

def load_state():
    """Load the state from a file."""
    try:
        with open('state.json', 'r') as f:
            state = json.load(f)
        link_combo.value = state.get('link_combo', 'aaaaa')
        total_requests.value = state.get('total_requests', 0)
        matched_urls_count.value = state.get('matched_urls_count', 0)
        entry_char_set.delete(0, tk.END)
        entry_char_set.insert(0, state.get('character_set', default_combo_set))
        messagebox.showinfo("Load State", "State loaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Error loading state: {e}")

# ---------------------------- Main Program Entry Point ----------------------------------------------------

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Needed for Windows

    # Initialize multiprocessing variables here
    stop_flag = multiprocessing.Value('b', False)
    pause_flag = multiprocessing.Value('b', False)
    total_requests = multiprocessing.Value('i', 0)
    matched_urls_queue = multiprocessing.Queue()
    matched_urls_count = multiprocessing.Value('i', 0)
    active_tasks_count = multiprocessing.Value('i', 0)
    link_combo = multiprocessing.Manager().Value(str, 'aaaaa')
    link_combo_lock = multiprocessing.Lock()
    base_urls = multiprocessing.Manager().list()
    links_per_minute = multiprocessing.Value('i', 0)

    # ---------------------------- GUI Setup ---------------------------------------------------------------

    root = tk.Tk()
    root.title("CloudHarvestDirect: Harvest Tool Beta 3 (Multi-Core)")
    root.configure(bg="#2e2e2e")

    # Style configurations
    widget_style_config = {"bg": "#2e2e2e", "fg": "#ffffff"}
    entry_style_config = {"bg": "#4d4d4d", "fg": "#ffffff", "insertbackground": "#ffffff", "font": ("Helvetica", 12)}
    frame_style_config = {"bg": "#2e2e2e"}

    # Frames for organization
    input_frame = tk.Frame(root, **frame_style_config)
    input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    control_frame = tk.Frame(root, **frame_style_config)
    control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    status_frame = tk.Frame(root, **frame_style_config)
    status_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    # ---------------------------- Input Fields ------------------------------------------------------------

    # Starting Point
    tk.Label(input_frame, text="Starting Point:", **widget_style_config, font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_starting_point = tk.Entry(input_frame, **entry_style_config)
    entry_starting_point.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    entry_starting_point.insert(0, 'aaaaa')

    # Character Set
    tk.Label(input_frame, text="Character Set:", **widget_style_config, font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_char_set = tk.Entry(input_frame, **entry_style_config)
    entry_char_set.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entry_char_set.insert(0, default_combo_set)

    # Concurrent Tasks per Process
    tk.Label(input_frame, text="Concurrent Tasks per Process:", **widget_style_config, font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    process_slider = tk.Scale(input_frame, from_=500, to=30000, orient=tk.HORIZONTAL, bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12), command=update_concurrency_limit)
    process_slider.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    process_slider.set(5000)  # Default value

    # Number of Processes
    tk.Label(input_frame, text="Number of Threads Detected:", **widget_style_config, font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_num_processes = tk.Entry(input_frame, **entry_style_config)
    entry_num_processes.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    entry_num_processes.insert(0, str(multiprocessing.cpu_count()))

    # Artist File
    tk.Label(input_frame, text="Artist File:", **widget_style_config, font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_artist_file = tk.Entry(input_frame, **entry_style_config)
    entry_artist_file.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    tk.Button(input_frame, text="Browse", command=lambda: select_artist_file(base_urls), font=("Helvetica", 12)).grid(row=4, column=2, padx=10, pady=5, sticky="w")

    # ---------------------------- Control Buttons ---------------------------------------------------------

    start_button = tk.Button(control_frame, text="Start", command=lambda: on_start(stop_flag, pause_flag, total_requests, matched_urls_queue, matched_urls_count, link_combo, link_combo_lock, base_urls, active_tasks_count), font=("Helvetica", 12), width=10)
    start_button.grid(row=0, column=0, padx=10, pady=10)

    pause_button = tk.Button(control_frame, text="Pause", command=lambda: on_pause(pause_flag), font=("Helvetica", 12), width=10, state=tk.DISABLED)
    pause_button.grid(row=0, column=1, padx=10, pady=10)

    stop_button = tk.Button(control_frame, text="Stop", command=lambda: on_stop(stop_flag), font=("Helvetica", 12), width=10, state=tk.DISABLED)
    stop_button.grid(row=0, column=2, padx=10, pady=10)

    tk.Button(control_frame, text="Save State", command=save_state, font=("Helvetica", 12), width=10).grid(row=1, column=0, padx=10, pady=5)
    tk.Button(control_frame, text="Load State", command=load_state, font=("Helvetica", 12), width=10).grid(row=1, column=1, padx=10, pady=5)

    # ---------------------------- Status Text -------------------------------------------------------------

    status_text_frame = tk.Frame(status_frame, **frame_style_config)
    status_text_frame.pack(fill=tk.BOTH, expand=True)

    text_style_config = {"bg": "#4d4d4d", "fg": "#ffffff", "insertbackground": "#ffffff", "font": ("Helvetica", 12)}
    status_text = tk.Text(status_text_frame, height=15, width=80, **text_style_config)
    status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    status_scroll = tk.Scrollbar(status_text_frame, command=status_text.yview)
    status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    status_text.config(yscrollcommand=status_scroll.set)

    # ---------------------------- Start the GUI Mainloop --------------------------------------------------

    root.mainloop()
    
    
    # ---------------------------------------- End -------------------------------------------------------------
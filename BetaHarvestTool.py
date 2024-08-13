import os
import asyncio
import aiohttp
import re
import string
import json
from urllib.parse import urlparse, urlunparse
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import multiprocessing
import queue
import time

# Global variable to store concurrency limit
concurrency_limit_value = multiprocessing.Value('i', 5000)

def update_concurrency_limit(val):
    with concurrency_limit_value.get_lock():
        concurrency_limit_value.value = int(val)

def increment_link_combo(combo, combo_set):
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
    try:
        async with session.get(url, allow_redirects=False) as response:
            return response, await response.text()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None, None

async def check_link(session, url, stop_flag, pause_flag, total_requests, matched_urls, base_urls):
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
            matched_urls.append(url_final)

async def worker(process_id, stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls):
    async with aiohttp.ClientSession() as session:
        tasks = set()
        while not stop_flag.value:
            with concurrency_limit_value.get_lock():
                concurrency_limit = concurrency_limit_value.value
            while len(tasks) < concurrency_limit and not stop_flag.value:
                with link_combo_lock:
                    url = f"https://on.soundcloud.com/{link_combo.value}"
                    link_combo.value = increment_link_combo(link_combo.value, combo_set)
                task = asyncio.create_task(check_link(session, url, stop_flag, pause_flag, total_requests, matched_urls, base_urls))
                tasks.add(task)
                task.add_done_callback(tasks.discard)
            await asyncio.sleep(0.1)

def process_worker(process_id, stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls):
    asyncio.run(worker(process_id, stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls))

def main(num_processes, stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls):
    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=process_worker, args=(i, stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    save_links(matched_urls)
    rename_output_file()

def save_links(matched_urls):
    with open("output.json", "w") as f:
        json.dump(list(matched_urls), f, indent=4)

def rename_output_file():
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"output_{date_str}.json"
    try:
        os.rename("output.json", new_filename)
        print(f"Output file renamed to: {new_filename}")
    except Exception as e:
        print(f"Failed to rename output file: {e}")

def on_start(stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls):
    global last_update_time, last_total_requests
    last_update_time = time.time()  # Initialize last update time
    last_total_requests = 0  # Initialize last total requests

    stop_flag.value = False
    pause_flag.value = False
    total_requests.value = 0
    matched_urls[:] = []
    link_combo.value = entry_starting_point.get()
    num_processes = multiprocessing.cpu_count()
    start_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)
    threading.Thread(target=lambda: main(num_processes, stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls), daemon=True).start()
    update_status_periodically(stop_flag, total_requests, matched_urls, link_combo)

def on_stop(stop_flag):
    stop_flag.value = True
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, "Stopping in progress...\n")
    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL)

def on_pause(pause_flag):
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

def update_status(stop_flag, total_requests, matched_urls, link_combo):
    global last_update_time, last_total_requests
    current_time = time.time()
    elapsed_time = current_time - last_update_time

    status_text.config(state=tk.NORMAL)
    status_text.delete("1.0", tk.END)
    status_text.insert(tk.END, f"Links Checked: {total_requests.value}\n")
    status_text.insert(tk.END, f"Links Found: {len(matched_urls)}\n")
    status_text.insert(tk.END, f"Current Link Combo: {link_combo.value}\n")

    if elapsed_time >= 60:  # Calculate links per minute every minute
        links_per_minute = total_requests.value - last_total_requests
        status_text.insert(tk.END, f"Links per Minute: {links_per_minute}\n")
        last_update_time = current_time
        last_total_requests = total_requests.value

    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)

def update_status_periodically(stop_flag, total_requests, matched_urls, link_combo):
    update_status(stop_flag, total_requests, matched_urls, link_combo)
    if not stop_flag.value:
        root.after(1000, update_status_periodically, stop_flag, total_requests, matched_urls, link_combo)

def select_artist_file(base_urls):
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

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Needed for Windows

    # Initialize multiprocessing variables here
    stop_flag = multiprocessing.Value('b', False)
    pause_flag = multiprocessing.Value('b', False)
    total_requests = multiprocessing.Value('i', 0)
    matched_urls = multiprocessing.Manager().list()
    link_combo = multiprocessing.Manager().Value(str, 'aaaaa')
    link_combo_lock = multiprocessing.Lock()
    base_urls = multiprocessing.Manager().list()
    combo_set = string.ascii_lowercase + string.ascii_uppercase + string.digits

    root = tk.Tk()
    root.title("CloudHarvestDirect: SoundCloud Link Checker (Multi-Core)")
    root.configure(bg="#2e2e2e")

    style_config = {"bg": "#2e2e2e", "fg": "#ffffff"}
    entry_config = {"bg": "#4d4d4d", "fg": "#ffffff", "insertbackground": "#ffffff", "font": ("Helvetica", 12)}

    tk.Label(root, text="Starting Point:", **style_config, font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_starting_point = tk.Entry(root, **entry_config)
    entry_starting_point.grid(row=0, column=1, padx=10, pady=10)
    entry_starting_point.insert(0, 'aaaaa')

    tk.Label(root, text="Concurrent Tasks per Core:", **style_config, font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    
    process_slider = tk.Scale(root, from_=500, to=30000, orient=tk.HORIZONTAL, **style_config, font=("Helvetica", 12), command=update_concurrency_limit)
    process_slider.grid(row=1, column=1, padx=10, pady=10)
    process_slider.set(5000)  # Default value

    tk.Label(root, text="Artist File:", **style_config, font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_artist_file = tk.Entry(root, **entry_config)
    entry_artist_file.grid(row=2, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: select_artist_file(base_urls), font=("Helvetica", 12)).grid(row=2, column=2, padx=10, pady=10)

    start_button = tk.Button(root, text="Start", command=lambda: on_start(stop_flag, pause_flag, total_requests, matched_urls, link_combo, link_combo_lock, combo_set, base_urls), font=("Helvetica", 12), width=10)
    start_button.grid(row=3, column=0, padx=10, pady=10)

    pause_button = tk.Button(root, text="Pause", command=lambda: on_pause(pause_flag), font=("Helvetica", 12), width=10, state=tk.DISABLED)
    pause_button.grid(row=3, column=1, padx=10, pady=10)

    stop_button = tk.Button(root, text="Stop", command=lambda: on_stop(stop_flag), font=("Helvetica", 12), width=10, state=tk.DISABLED)
    stop_button.grid(row=3, column=2, padx=10, pady=10)

    frame_style_config = {"bg": "#2e2e2e"}
    status_frame = tk.Frame(root, **frame_style_config)
    status_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="w")

    text_style_config = {"bg": "#4d4d4d", "fg": "#ffffff", "insertbackground": "#ffffff", "font": ("Helvetica", 12)}
    status_text = tk.Text(status_frame, height=10, width=50, **text_style_config)
    status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    status_scroll = tk.Scrollbar(status_frame, command=status_text.yview)
    status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    status_text.config(yscrollcommand=status_scroll.set)

    root.mainloop()

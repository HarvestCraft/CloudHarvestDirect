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

# Global variables
stop_flag = False
pause_flag = False
total_requests = 0
matched_urls = []
link_combo = 'aaaaa'
concurrency_limit = 1500
base_urls = []
combo_set = string.ascii_lowercase + string.ascii_uppercase + string.digits
link_combo_lock = threading.Lock()

def increment_link_combo(combo):
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
        combo_list = [combo_set[0]] * (len(combo_list) + 1)  # Extend the length when all positions overflow
    return ''.join(combo_list)

async def fetch_url(session, url):
    try:
        async with session.get(url, allow_redirects=False) as response:
            return response, await response.text()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None, None

async def check_link(session, url):
    global total_requests, matched_urls

    while pause_flag:
        await asyncio.sleep(1)  # Pause the loop when pause_flag is set

    if stop_flag:
        return  # Stop if the flag is set

    response, text = await fetch_url(session, url)
    total_requests += 1

    if response and response.status == 302:
        full_url = response.headers.get('Location', '')
        url_final = urlunparse(urlparse(full_url)._replace(query=''))
        match = re.search(r'/s-[a-zA-Z0-9]{11}', url_final)
        if match and (not base_urls or any(base_url in url_final for base_url in base_urls)):
            matched_urls.append(url_final)
            if len(matched_urls) % 100 == 0:
                save_links()

    update_status()

async def main():
    global stop_flag, link_combo

    async with aiohttp.ClientSession() as session:
        tasks = []
        while not stop_flag:
            while len(tasks) < concurrency_limit and not stop_flag:
                with link_combo_lock:
                    url = f"https://on.soundcloud.com/{link_combo}"
                    link_combo = increment_link_combo(link_combo)
                tasks.append(asyncio.create_task(check_link(session, url)))

            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks = list(pending)

        # Wait for remaining tasks to complete before fully stopping
        await asyncio.gather(*tasks, return_exceptions=True)

    save_links()
    rename_output_file()  # Rename after saving final output

def save_links():
    with open("output.json", "w") as f:
        json.dump(matched_urls, f, indent=4)
    print(f"\nOutput File: output.json")

def rename_output_file():
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"output_{date_str}.json"
    try:
        os.rename("output.json", new_filename)
        print(f"Output file renamed to: {new_filename}")
    except Exception as e:
        print(f"Failed to rename output file: {e}")

def on_start():
    global stop_flag, pause_flag, total_requests, matched_urls, link_combo, concurrency_limit
    stop_flag = False
    pause_flag = False
    total_requests = 0
    matched_urls = []
    link_combo = entry_starting_point.get()
    concurrency_limit = int(entry_process_count.get())
    start_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)
    threading.Thread(target=run_main).start()

def run_main():
    asyncio.run(main())

def on_stop():
    global stop_flag
    stop_flag = True
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, "Stopping in progress...\n")
    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL)

def on_pause():
    global pause_flag
    pause_flag = not pause_flag
    if pause_flag:
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

def update_status():
    status_text.config(state=tk.NORMAL)
    status_text.delete("1.0", tk.END)
    status_text.insert(tk.END, f"Links Checked: {total_requests}\n")
    status_text.insert(tk.END, f"Links Found: {len(matched_urls)}\n")
    status_text.insert(tk.END, f"Current Link Combo: {link_combo}\n")
    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)
    root.update_idletasks()

def select_artist_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        entry_artist_file.delete(0, tk.END)
        entry_artist_file.insert(0, file_path)
        global base_urls
        try:
            with open(file_path, "r") as f:
                base_urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Error reading base URLs file: {e}")
    else:
        base_urls.clear()

if __name__ == "__main__":
    # Create GUI
    root = tk.Tk()
    root.title("CloudHarvestDirect: SoundCloud Link Checker")
    root.configure(bg="#2e2e2e")

    # Style configurations for dark mode
    style_config = {
        "bg": "#2e2e2e",
        "fg": "#ffffff",
    }

    entry_config = {
        "bg": "#4d4d4d",
        "fg": "#ffffff",
        "insertbackground": "#ffffff",
        "font": ("Helvetica", 12)
    }

    tk.Label(root, text="Starting Point:", **style_config, font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_starting_point = tk.Entry(root, **entry_config)
    entry_starting_point.grid(row=0, column=1, padx=10, pady=10)
    entry_starting_point.insert(0, 'aaaaa')

    tk.Label(root, text="Process Count:", **style_config, font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_process_count = tk.Entry(root, **entry_config)
    entry_process_count.grid(row=1, column=1, padx=10, pady=10)
    entry_process_count.insert(0, '5000')

    tk.Label(root, text="Artist File:", **style_config, font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_artist_file = tk.Entry(root, **entry_config)
    entry_artist_file.grid(row=2, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=select_artist_file, font=("Helvetica", 12)).grid(row=2, column=2, padx=10, pady=10)

    start_button = tk.Button(root, text="Start", command=on_start, font=("Helvetica", 12), width=10)
    start_button.grid(row=3, column=0, padx=10, pady=10)

    pause_button = tk.Button(root, text="Pause", command=on_pause, font=("Helvetica", 12), width=10, state=tk.DISABLED)
    pause_button.grid(row=3, column=1, padx=10, pady=10)

    stop_button = tk.Button(root, text="Stop", command=on_stop, font=("Helvetica", 12), width=10, state=tk.DISABLED)
    stop_button.grid(row=3, column=2, padx=10, pady=10)

    # Create a frame for the status text
    frame_style_config = {
        "bg": "#2e2e2e"
    }
    status_frame = tk.Frame(root, **frame_style_config)
    status_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="w")

    text_style_config = {
        "bg": "#4d4d4d",
        "fg": "#ffffff",
        "insertbackground": "#ffffff",
        "font": ("Helvetica", 12)
    }
    status_text = tk.Text(status_frame, height=10, width=50, **text_style_config)
    status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    status_scroll = tk.Scrollbar(status_frame, command=status_text.yview)
    status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    status_text.config(yscrollcommand=status_scroll.set)

    root.mainloop()


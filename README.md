---
<p align="center">
  <img src="https://imgur.com/n0OSbBP.png" alt="CloudHarvestDirect Logo" width="350">
</p>

<h1 align="center">
  CloudHarvestDirect™
</h1>

## Overview

CloudHarvestDirect is a powerful tool designed to automate the process of checking SoundCloud links to find private or hidden tracks. It generates combinations of link identifiers, checks if they redirect to valid SoundCloud URLs, and saves any valid matches to an output file. The script includes a graphical user interface (GUI) built with `tkinter` for ease of use.

## **Deprecated Versions**

**Note:** The initial HarvestTool.py & BetaHarvestTool.py version of CloudHarvestDirect are now deprecated. Users are encouraged to upgrade to **Beta 3**, which includes significant improvements in performance, usability, and functionality.


## Table of Contents

- [Overview](#overview)
- [Deprecated Versions](#deprecated-versions)
- [Key Changes in Beta 3](#key-changes-in-beta-3)
  - [1. Code Organization and Structure](#1-code-organization-and-structure)
  - [2. Improved Concurrency Handling](#2-improved-concurrency-handling)
  - [3. Matched URLs Storage and Saving](#3-matched-urls-storage-and-saving)
  - [4. GUI Enhancements](#4-gui-enhancements)
  - [5. Save and Load State Functionality](#5-save-and-load-state-functionality)
  - [6. Character Set Customization](#6-character-set-customization)
  - [7. Performance Improvements](#7-performance-improvements)
  - [8. Code Comments and Documentation](#8-code-comments-and-documentation)
- [Conclusion](#conclusion)
- [Features](#features)
- [Creating an Artist File](#creating-an-artist-file)
  - [Purpose](#purpose)
  - [Format](#format)
  - [Usage](#usage)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps to Use on Windows](#steps-to-use-on-windows)
  - [Steps to Use on Mac](#steps-to-use-on-mac)
- [Screenshots](#screenshots)
  - [Default Link Checker GUI](#default-link-checker-gui)
  - [Link Checker in Use](#link-checker-in-use)
  - [CloudHarvestDirect Link Searcher](#cloudharvestdirect-link-searcher)
- [Technical Details](#technical-details)
  - [Vulnerability Overview](#vulnerability-overview)
  - [Script Functionality](#script-functionality)
  - [Handling Duplicate Links](#handling-duplicate-links)
  - [False Positives](#false-positives)
- [Credits](#credits)


## Key Changes in Beta 3

This document outlines the new changes introduced in **Beta 3** of the **CloudHarvestDirect Harvest Tool**, compared to the initial beta version. The enhancements focus on improving performance, usability, and functionality of the tool.

---


### Key Changes in Beta 3

#### 1. Code Organization and Structure

- **Modular Import Statements**: The import statements are now organized into sections, improving readability and maintainability.
- **Clear Global Variables**: Global variables are better organized, with descriptive names and comments explaining their purpose.
- **Function Definitions with Comments**: Functions are clearly defined with accompanying comments that explain their functionality, making the codebase easier to understand.
- **Structured Main Entry Point**: The main execution logic is encapsulated under the `if __name__ == "__main__":` block, following Python best practices.

#### 2. Improved Concurrency Handling

- **Active Tasks Counting**: Introduced counting of active asynchronous tasks to monitor the number of currently running tasks.
- **Dynamic Concurrency Limit**: The concurrency limit per process can still be adjusted via the GUI slider and is now dynamically applied to control task execution effectively.
- **Active Task Decrement Function**: A new function `decrement_active_tasks` accurately tracks task completion, ensuring reliable active task counts.
- **Process and Task Management**: Enhanced management of processes and tasks leads to better resource utilization and prevents overloading the system.

#### 3. Matched URLs Storage and Saving

- **Use of Multiprocessing Queue**: Replaced `multiprocessing.Manager().list()` with `multiprocessing.Queue()` for storing matched URLs, resulting in improved performance and thread safety.
- **Dedicated Saver Thread**: Implemented a saver thread that continuously writes matched URLs to an output file as they are found, ensuring data is not lost upon interruption.
- **Real-Time Links per Minute Calculation**: The saver thread calculates and updates the number of links checked per minute, providing users with real-time performance metrics.

#### 4. GUI Enhancements

- **Additional Input Fields**:
  - **Character Set Input**: Users can now specify the character set used for generating link combinations directly from the GUI.
  - **Number of Processes Input**: Users can define the number of processes (threads) to utilize, allowing customization based on system capabilities.
- **Enhanced Status Information**: The GUI now displays detailed status information, including:
  - Total links checked.
  - Number of links found.
  - Links checked per minute.
  - Current link combination being tested.
  - Number of processes and concurrency per process.
  - Maximum and active tasks running on the machine.
  - Character set currently in use.
- **Improved Layout and Readability**: The GUI components are organized into frames, enhancing the overall layout and user experience.

#### 5. Save and Load State Functionality

- **Save State Feature**: Users can save the current state of the tool, capturing essential parameters such as:
  - Current link combination.
  - Total requests made.
  - Matched URLs count.
  - Character set in use.
- **Load State Feature**: Users can load a previously saved state to resume scanning from where they left off, facilitating long-running scans and providing resilience against interruptions.

#### 6. Character Set Customization

- **User-Defined Character Sets**: The tool now allows users to input a custom character set for generating link combinations, enabling more targeted or exhaustive scans.
- **Validation of Character Set Input**: Input validation ensures that the character set is not empty, preventing runtime errors.

#### 7. Performance Improvements

- **Optimized Asynchronous I/O**: Code optimizations have been made to the asynchronous functions, improving the efficiency of network operations.
- **Efficient Task Scheduling**: Improved task management logic leads to better scheduling and execution of tasks, reducing idle times and increasing throughput.
- **Reduced Overhead**: Switching to a multiprocessing queue for matched URLs and introducing a dedicated saver thread reduces inter-process communication overhead.

#### 8. Code Comments and Documentation

- **Comprehensive Inline Comments**: The codebase now includes detailed inline comments that explain the functionality of code blocks and individual lines where necessary.
- **Function Documentation**: Each function is accompanied by a docstring or comment that describes its purpose, inputs, and outputs.
- **Section Headers**: The code is divided into logical sections with headers, making navigation and understanding of the code structure more straightforward.

---

### Conclusion

The Beta 3 release of the **CloudHarvestDirect Harvest Tool** brings substantial improvements over the initial beta version. The enhancements focus on:

- **Performance**: Optimizations in concurrency handling and task management lead to faster scanning and better resource utilization.
- **Usability**: GUI enhancements and new features like save/load state and character set customization provide users with more control and flexibility.
- **Reliability**: The introduction of a saver thread and improved error handling ensures that matched URLs are not lost and the tool can recover from interruptions.

Users are encouraged to upgrade to Beta 3 to take advantage of these new features and improvements.

---

Thank you for using **CloudHarvestDirect Harvest Tool Beta 3**. If you encounter any issues or have suggestions for further improvements, please open an issue on the GitHub repository.

## Features

- **Concurrency**: Efficiently handles a high number of concurrent requests for large-scale link checking.
- **User-Friendly GUI**: Start, stop, and monitor the progress of your link checking tasks through an intuitive interface.
- **Customizable Starting Point**: Define a starting point for the link combinations to focus on specific segments of the identifier space.
- **Artist File Integration**: Narrow down your search by focusing on specific artists through an easy-to-create artist file.
- **Save and Load State**: Save your progress and resume scanning from where you left off.
- **Character Set Customization**: Specify a custom character set for generating link combinations.

## Creating an Artist File

### Purpose

An artist `.txt` file allows you to target your search to links associated with specific artists, avoiding unrelated private links. This feature is particularly useful when you want to focus on specific artists.

### Format

- Each line in the artist file should contain the full URL of the artist's SoundCloud page, ending with a `/`.
- Example entry: `https://soundcloud.com/artistname/`
- The trailing slash at the end of the artist URL ensures that only exact matches are considered.
- **File Format**: Save the file with a `.txt` extension.

### Usage

- **Including an Artist File**: When an artist file is included, the script will only save private links that match the URLs listed in the file.
- **No Artist File Provided**: If no artist file is provided, the script will save all discovered private links.

## Installation

### Prerequisites

- Python 3.x installed on your machine.
- Basic command line knowledge.
- Required Python packages:
  - `aiohttp`
  - `tkinter` (usually comes pre-installed with Python)


### Steps to Use on Windows:

1. Open the command prompt.
2. Navigate to the folder containing the script using `cd PATH_TO_FOLDER_WITH_SCRIPT`.
3. Run the script with `python HarvestTool.py`.

### Steps to Use on Mac:

1. *No fucking idea, I'm poor.*
2. You MUST install ` install certificates.command ` from the python folder on your mac or you will get SSL errors. 

## Screenshots

### Default Link Checker GUI

<p align="center">
  <img src="https://imgur.com/UtrJm6C.png" alt="Default Link Checker GUI" width="400">
  <img src="https://imgur.com/Ka3xuRS.png" alt="Mac Version of Link Checker GUI" width="480">
</p>

### Link Checker in Use

<p align="center">
  <img src="https://imgur.com/HqKjzG0.png" alt="Link Checker in Use" width="400">
</p>

## CloudHarvestDirect Link Searcher:

CloudHarvestDirect Link Searcher is a simple and efficient tool for searching through a master list of SoundCloud links. The tool is designed to help you quickly find specific links from a large dataset, with features that allow you to save your search results as a text file.

### Features

- **Dark Mode Interface**: A sleek, dark-themed user interface for comfortable use.
- **Master Links File Selection**: Easily load your master list of SoundCloud links via a file selection dialog.
- **Efficient Search**: Quickly search through millions of links using built-in search functionality.
- **Save Search Results**: Save your search results to a text file, with the ability to name the file as desired.
- **Clear Search Results**: Clear your current search results with a single click to start fresh.
- **Logbox Notifications**: Get real-time feedback on the tool's operations through the logbox at the bottom of the interface.

### Screenshot

<p align="center">
  <img src="https://imgur.com/SJcdgLZ.png" alt="CloudHarvestDirect Link Searcher" width="400">
</p>

**Note:** The program may appear unresponsive while loading a large master links file. Please wait for about 30 seconds.



---

## Technical Details

### Vulnerability Overview

- **Link Structure**: SoundCloud uses shortened links (e.g., `https://on.soundcloud.com/xxxxx`) where `xxxxx` is a five-character identifier.
- **Brute-Force Potential**: The identifier can be brute-forced to find valid links to private content. Although there are theoretically 916 million possible combinations, the actual number is lower due to restrictions such as:
  - Identifiers cannot start with a 0.
  - Certain characters or combinations might be excluded for usability or aesthetic reasons.
  - Additional internal rules may further limit valid identifiers.

### Script Functionality

- **Link Generation**: The script generates all possible combinations of the identifier within the defined constraints.
- **Link Testing**: Each generated link is tested to determine if it corresponds to a valid private track or playlist. This is achieved by catching the redirect (HTTP 302 response) from the shortened link to the full SoundCloud URL.
- **Private Content Detection**: A regex is used to identify if the full link contains a private token, which is unique to private tracks and playlists.
- **Output Handling**: Valid private links are saved in a JSON file for further review or action.

### Handling Duplicate Links

- **Duplicate Links**: Duplicates may occur due to redirection caching, multiple identifiers for the same track, or network latency. The script handles these, but repeated entries may still appear.

### False Positives

The regex filter may cause some false positives, such as:

- **Old Private Tracks**: Tracks that were once private but are now public may still retain the private token in their URLs.
- **Deleted Tracks**: Links to deleted tracks might also match the regex, leading to incorrect identification as private content.

---
## Credits

- **Script Development**: Original random link finding version credited to [3eyka](https://github.com/3eyka/sound-cloudripper) and [fancymalware](https://github.com/fancymalware/soundcloud-ripper). Thank you for the inspiration!

---


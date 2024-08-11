<p align="center">
  <img src="https://imgur.com/n0OSbBP.png" alt=" CloudHarvestDirect™ Logo" width="200">
</p>

<h1 align="center">
   CloudHarvestDirect™™
</h1>

## Overview

 CloudHarvestDirect™ is a powerful tool designed to automate the process of checking SoundCloud links to find private or hidden tracks. It generates combinations of link identifiers, checks if they redirect to valid SoundCloud URLs, and saves any valid matches to an output file. The script includes a graphical user interface (GUI) built with `tkinter` for ease of use.

## Features

- **Concurrency**: Efficiently handles a high number of concurrent requests for large-scale link checking.
- **User-Friendly GUI**: Start, stop, and monitor the progress of your link checking tasks through an intuitive interface.
- **Customizable Starting Point**: Define a starting point for the link combinations to focus on specific segments of the identifier space.
- **Artist File Integration**: Narrow down your search by focusing on specific artists through an easy-to-create artist file.

## Creating an Artist File

### Purpose

An artist file allows you to target your search to links associated with specific artists, avoiding unrelated private links. This feature is particularly useful when you want to focus on specific artists.

### Format

- Each line in the artist file should contain the full URL of the artist's SoundCloud page, ending with a `/`.
- Example entry: `https://soundcloud.com/artistname/`
- The trailing slash at the end of the artist URL ensures that only exact matches are considered. For example, `https://soundcloud.com/artistname/` will not mistakenly match `https://soundcloud.com/artistname123/`, which is a different artist.
- It's recommended to include as many artists as possible to maximize the search's relevance.

### Usage

- **Including an Artist File**: When an artist file is included, the script will only save private links that match the URLs listed in the file.
- **No Artist File Provided**: If no artist file is provided, the script will save all discovered private links.

## Installation

### Prerequisites

- Python 3.x installed on your machine.
- Basic command line knowledge.

### Steps to Use on Windows

1. Open the command prompt.
2. Navigate to the folder containing the script using `cd PATH_TO_FOLDER_WITH_SCRIPT`.
3. Run the script with `python HarvestTool.py`.

### Steps to Use on Mac

1. No fucking idea I'm poor.




### Default Link Checker GUI

<p align="center">
  <img src="https://imgur.com/UtrJm6C.png" alt="Default Link Checker GUI" width="400">
  <img src="https://imgur.com/Ka3xuRS.png" alt="Mac Version of Link Checker GUI" width="480">
</p>

### Link Checker in Use

<p align="center">
  <img src="https://imgur.com/HqKjzG0.png" alt="Link Checker in Use" width="400">
</p>

#  CloudHarvestDirect™ Link Searcher

 CloudHarvestDirect™ Link Searcher is a simple and efficient tool for searching through a master list of SoundCloud links. The tool is designed to help you quickly find specific links from a large dataset, with features that allow you to save your search results as a text file.

## Features

- **Dark Mode Interface**: A sleek, dark-themed user interface for comfortable use.
- **Master Links File Selection**: Easily load your master list of SoundCloud links via a file selection dialog.
- **Efficient Search**: Quickly search through millions of links using built-in search functionality.
- **Save Search Results**: Save your search results to a text file, with the ability to name the file as desired.
- **Clear Search Results**: Clear your current search results with a single click to start fresh.
- **Logbox Notifications**: Get real-time feedback on the tool's operations through the logbox at the bottom of the interface.


<p align="center">
  <img src="https://imgur.com/SJcdgLZ.png" alt=" CloudHarvestDirect™ Link Searcher" width="400">
</p>

**Note:** The program may appear unresponsive while loading a large master links file. Please wait for about 30 seconds.


### Technical Details

#### Vulnerability Overview

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

#### Handling Duplicate Links

- **Duplicate Links**: Duplicates may occur due to redirection caching, multiple identifiers for the same track, or network latency. The script handles these, but repeated entries may still appear.

### False Positives

The regex filter may cause some false positives, such as:

- **Old Private Tracks**: Tracks that were once private but are now public may still retain the private token in their URLs.
- **Deleted Tracks**: Links to deleted tracks might also match the regex, leading to incorrect identification as private content.




## Credits

- **Script Development**: Original random link finding version credited to [3eyka](https://github.com/3eyka/sound-cloudripper) and [fancymalware](https://github.com/fancymalware/soundcloud-ripper). Thank you for the inspiration!

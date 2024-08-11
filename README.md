# CloudHarvestDirect

## Overview

This script is designed to automate the process of checking SoundCloud links to find private or hidden tracks. It generates combinations of link identifiers, checks if they redirect to valid SoundCloud URLs, and saves any valid matches to an output file. The script includes a graphical user interface (GUI) built with `tkinter` for ease of use.

## Features

- **Concurrency**: The script can handle a high number of concurrent requests, making it efficient for large-scale link checking.
- **GUI**: A user-friendly interface for starting, stopping, and monitoring the progress of the link checker.
- **Customizable Starting Point**: Allows you to define a starting point for the link combinations.
- **Artist File Integration**: You can provide a file with specific artist URLs to focus the search on relevant links.



## Creating an Artist File

### Purpose

An artist file allows you to narrow down the search to links associated with specific artists. This is useful when you want to focus on particular artists and avoid unrelated private links.

### Format

- Each line in the artist file should contain the full URL of the artist's SoundCloud page, ending with a `/`.
- Example entry: https://soundcloud.com/artistname/
- The trailing slash at the end of the artist URL ensures that only exact matches are considered. For example, `https://soundcloud.com/artistname/` will not mistakenly match `https://soundcloud.com/artistname123/`, which is a different artist.


### Usage

- **Including an Artist File**: When you include an artist file, the script will only save private links that match the URLs listed in the file.
- **No Artist File Provided**: If no artist file is provided, the script will save all discovered private links.


## Installation

### Prerequisites

- Python 3.x installed on your machine.
- Basic understanding of how to use the command line.

### Steps to Use

1. Open the command prompt.
2. Navigate to the folder containing the script using `cd PATH_TO_FOLDER_WITH_SCRIPT`.
3. Run the script with `python HarvestTool.py`.



## Screenshots

### Default Link Checker GUI

![Default Link Checker](https://imgur.com/aJYsfGk.png)

### Link Checker in Use

![Link Checker in Use](https://imgur.com/lKjxNGi.png)


## Bug Report: Insecure Direct Object Reference (IDOR) Vulnerability in SoundCloud Shareable Links

### Report Summary

- **Platform**: SoundCloud
- **Affected URLs**: `https://on.soundcloud.com/xxxxx`
- **Summary**: 
- A vulnerability has been identified in SoundCloud's link system that allows unauthorized access to private tracks and playlists through insecure direct object references (IDOR). By brute-forcing the five-character identifier in shareable links, an attacker can discover valid URLs leading to private content. This report details the exploit, its impact, and proposed mitigations.

### Technical Details

#### Vulnerability Overview

 **Link Structure**: SoundCloud uses shortened links (e.g., `https://on.soundcloud.com/xxxxx`) where `xxxxx` is a five-character identifier.
 **Brute-Force Potential**: The identifier can be brute-forced to find valid links to private content. Although there are theoretically 916 million possible combinations, the actual number is lower due to restrictions such as:
- Identifiers cannot start with a digit.
- Certain characters or combinations might be excluded for usability or aesthetic reasons.
- Additional internal rules may further limit valid identifiers.

#### Script Functionality

 **Link Generation**: 
- The script generates all possible combinations of the identifier within the defined constraints.
 **Link Testing**:
- Each generated link is tested to determine if it corresponds to a valid private track or playlist.
- This is achieved by catching the redirect (HTTP 302 response) from the shortened link to the full SoundCloud URL.
 **Private Content Detection**:
- A regex is used to identify if the full link contains a private token, which is unique to private tracks and playlists.
 **Output Handling**:
- Valid private links are saved in a JSON file, documenting them for further review or action.
- **Duplicate Links**:
- Duplicates may occur due to redirection caching, multiple identifiers for the same track, or network latency. These are handled by the script but may still result in repeated entries.

#### False Positives

## The regex filter may cause some false positives, such as:
- **Old Private Tracks**: Tracks that were once private but are now public may still retain the private token in their URLs.
- **Deleted Tracks**: Links to deleted tracks might also match the regex, leading to incorrect identification as private content.






## Credits

- **Script Development**: Original script and random version credited to [3eyka](https://github.com/3eyka/sound-cloudripper) and [fancymalware](https://github.com/fancymalware/soundcloud-ripper) <3

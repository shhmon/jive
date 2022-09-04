# Jive

A simple middleware tool for version controlling Ableton Live projects with git

## Setup

1. Clone this repository
2. Add an alias to your `~/.bash_profile`: `alias jive="python3 /path/to/repo/main.py "`

## Usage

Currently the tool doesnt do much except collect your live set dependencies and translate .als files to .xml

- `jive init`: Initializes the .jive folder with a git repo inside
- `jive collect`: Collects sample dependencies into local samples folder and updates references in .als files
- `jive push`: Pushes the current project files to the .jive folder (translates .als files to .xml)
- `jive <any git action>`: Executes the git action in the .jive folder

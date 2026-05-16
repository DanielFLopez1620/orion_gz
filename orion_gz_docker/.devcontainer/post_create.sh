#!/bin/bash
set -e

echo "Importing repos..."
vcs import src < .devcontainer/repos.yaml

rosdep update
rosdep install --from-paths src --ignore-src -y
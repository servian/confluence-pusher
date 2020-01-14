#!/bin/sh
brew update;
brew doctor;
brew cleanup;
brew install python3 pandoc pandoc-citeproc;
pip install atlassian-python-api;
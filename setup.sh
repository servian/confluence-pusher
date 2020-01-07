#!/bin/sh
brew update;
brew doctor;
brew cleanup;
brew install gcc python3 atlassian-cli;
brew install pandoc pandoc-citeproc;
pip install confluence-command-line;
pip install pypandoc;
pip install atlassian-python-api;
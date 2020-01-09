#!/bin/sh
brew update;
brew doctor;
brew cleanup;
brew install gcc python3 atlassian-cli;
brew install pandoc pandoc-citeproc;
brew install cairo libffi;
pip install confluence-command-line;
# pip install pypandoc;
pip install atlassian-python-api;
pip install cairosvg;
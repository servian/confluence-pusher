#!/bin/sh
brew update;
brew doctor;
brew cleanup;
brew install gcc pandoc python3 atlassian-cli;
pip install confluence-command-line;
pip install HTMLParser;
pip install feedparser;
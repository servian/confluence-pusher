#!/bin/bash

# Import credentials as env variables
source .env

# Clean html/ folder
rm -rf html/*

# Convert markdown to html
for i in $(find . -name $MARKDOWN_EXTENSION);
  do mkdir -p html/$(dirname ${i:2}); pandoc $i -f markdown -s -o html/${i:2}.$HTML_EXTENSION;
done

# Convert links to svg files to svg data
python svg2html.py

# Cleanup:
# now rename html/*tmp to html
for i in $(find html -name "*.tmp");
  do mv $i ${i%????};
done

# Download https://bobswift.atlassian.net/wiki/spaces/ACLI/pages/16875586/Downloads
# Upload html/* to confluence
cd html
for i in $(find . -name "$HTML_EXTENSION");
  do ../acli.sh confluencecloud -a storePage --file $i --space $CONFLUENCE_SPACE --title ${i:2} -s $CONFLUENCE_WIKI_LINK --user $CONFLUENCE_USER --token $CONFLUENCE_TOKEN --replace --parent $CONFLUENCE_PARENT;
done

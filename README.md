# confluence-pusher

A tool to convert and upload markdown documents into Atlassian Confluence using [Atlassian Python API](https://atlassian-python-api.readthedocs.io/en/latest/index.html).

## How it works

### The flow

Read SOURCE_FOLDER --> Create empty document tree in Confluence --> Resize and attach SVG images --> Upload page contents into Confluence and rename document titles

### File conversion

It looks over the folder defined in SOURCE_FOLDER parameter in **config.py** and then traversing it looking for markdown files. The folder and document structure are being replicated in Confluence as follows with the document conversion being performed by Pandoc using [this](https://github.com/jpbarrette/pandoc-confluence-writer/blob/master/confluence.lua) custom filter:

|Local filesystem|Action|
| ------------- | ----------- |
|SOURCE_FOLDER: |Root document as defined by SOURCE_FOLDER parameter in **config.py**
|> file01.md    |Markdown file to be converted into nesting document under SOURCE_FOLDER name
|> file02.md    |The markdown headers are being read during the conversion. If not available, file02 is going to be used with markdown file extension dropped
|> README.md    |Will be converted in root document content
|> directory01: |Section document
|>>> file03.md  |Markdown file to be converted into nesting document under directory01 name with the same rules as above
|>>> README.md  |Will be converted in section content. The section document is to be renamed with markdown header if available

## How to use

### Configure Confluence API token

Configure your Confluence API token [here](https://id.atlassian.com/manage/api-tokens). More help [here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html).

## Install - Mac OS X

Install [Brew](https://brew.sh/):

```bash
/usr/bin/ruby -e "\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Run setup.sh:

```bash
sh setup.sh
```

## Configure

Get your wiki link and space name:

![Confluence link example](./img/configuration.svg)

### Update following parameters in **config.py**

```properties
CONFLUENCE_SPACE = "000000000";
CONFLUENCE_WIKI_LINK = "https://domain.atlassian.net/wiki";
CONFLUENCE_USER = "xxx.xxx@domain.com.au"
CONFLUENCE_TOKEN =  "XXX"
```

## Run

Once you configured your credentials in credentials.sh simply run:

```bash
python3 main.py
```

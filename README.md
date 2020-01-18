# confluence-pusher

A tool to convert and upload markdown documents into Atlassian Confluence using [Atlassian Python API](https://atlassian-python-api.readthedocs.io/en/latest/index.html).

---

## How it works

### The flow

![the flow](img/flow.svg)

### File conversion

**Please note that Confluence can't create two documents with the same name in the same space, for example: folder /Build and file named build.md**

It looks over the folder defined in SOURCE_FOLDER parameter in **config.json** and then traversing it looking for markdown files. The folder and document structure are being replicated in Confluence as follows with the document conversion being performed by Pandoc using [this](https://github.com/jpbarrette/pandoc-confluence-writer/blob/master/confluence.lua) custom filter:

|Local filesystem|Action|
| ------------- | ----------- |
|SOURCE_FOLDER: |Root document as defined by SOURCE_FOLDER parameter in **config.json**
|- file01.md    |Markdown file to be converted into nesting document under SOURCE_FOLDER name
|- file02.md    |The markdown headers are being read during the conversion. If not available, file02 is going to be used with markdown file extension dropped
|- README.md    |Will be converted in root document content
|- directory01: |Section document
|-- file03.md  |Markdown file to be converted into nesting document under directory01 name with the same rules as above
|-- README.md  |Will be converted in section content. The section document is to be renamed with markdown header if available

---

## Before you begin

### Configure Confluence API token [here](https://id.atlassian.com/manage/api-tokens). More help [here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html).

---

## Install

### Install from PyPi:

```bash
pip install confluence-pusher
```

### Install and run from the source code - Mac OS X

Install [Brew](https://brew.sh/):

```bash
/usr/bin/ruby -e "\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Run setup.sh:

```bash
sh setup.sh
```

---

## Configure

Get your wiki link and space name:

![Confluence link example](./img/configuration.svg)

### Update following parameters in **config.json**

```json
{
    "CONFLUENCE_SPACE": "",
    "CONFLUENCE_URL": "https://domain.atlassian.net",
    "CONFLUENCE_USERID": "your.email@domain.com",
    "CONFLUENCE_OATOKEN": "",
    "DELETE_ROOT_DOCUMENT_ON_STARTUP": true
}
```

---

## Run

Once you configured your credentials in credentials.sh simply run:

```bash
python3 cfpusher.py -s ../dir
```

where **../dir** is your folder with markdown files.

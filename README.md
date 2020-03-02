# confluence-pusher

A tool to convert and upload markdown documents into Atlassian Confluence using the [Atlassian Python API](https://atlassian-python-api.readthedocs.io/en/latest/index.html).

---

## How it works

### File conversion

> **Warning:** Confluence can't create two documents with the same name in the same space, for example: folder /Build and file named build.md

The source folder is traversed for markdown files. The folder and document structures are replicated in Confluence. The document conversion is performed using Pandoc with the [pandoc-confluence-writer](https://github.com/jpbarrette/pandoc-confluence-writer/blob/master/confluence.lua) custom filter:

| Local         | Confluence                   |
| :------------ | :--------------------------- |
| Root Folder   | Root Document                |
| README.md     | Root Document Content        |
| others.md     | Sub-Page under Root Document |
| Sub-Directory | Section Document             |

The document names are renamed to reflect the H1 markdown header if available.

---

## Before you begin

Configure Confluence API

- <https://id.atlassian.com/manage/api-tokens>
- <https://confluence.atlassian.com/cloud/api-tokens-938839638.html>

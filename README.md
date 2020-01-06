# confluence-pusher

A tool to convert documentation from variety of formats and upload content to Confluence.

# 1.Installation

1.1. Install [Brew](https://brew.sh/):

    /usr/bin/ruby -e "\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

1.2 Run setup.sh:

    sh setup.sh

# 2.Configuration

Change your confluence credentials in credentials.sh:

2.1. To get your wiki link and space name:

![Confluence link example](./img/configuration.svg)

    CONFLUENCE_SPACE = "xx";
    CONFLUENCE_WIKI_LINK = "https://vibrato.atlassian.net/wiki";

2.2. Use your email address for CONFLUENCE_USER:

    CONFLUENCE_USER = "xxx.xxx@vibrato.com.au"

2.3. Follow [this link](https://id.atlassian.com/manage/api-tokens) to configure your API token as described [here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html).

    CONFLUENCE_TOKEN =  "Cc7kbbR4VwyNXDh11K1PAEAA"

2.4. Parent page ID for your wiki or documentation. Read [this](https://confluence.atlassian.com/doc/create-and-edit-pages-139476.html) to learn how to create it.

    CONFLUENCE_PARENT = "684917000"

# 3.Run

Once you configured your credentials in credentials.sh simply run:

    sh run.sh

SOURCE_FOLDER = ""
CONFLUENCE_SPACE = ''
CONFLUENCE_URL = ''
CONFLUENCE_USERID = ''
CONFLUENCE_OATOKEN = ''
CONFLUENCE_SECTION_CONTENT_FILE = "README.md"
CONFLUENCE_TABLE_OF_CONTENTS = "SUMMARY.md"
DELETE_ROOT_DOCUMENT_ON_STARTUP = True


CONFLUENCE_FILTER_NAME = 'confluence.lua'
CONFLUENCE_FILTER_URL = "https://raw.githubusercontent.com/jpbarrette/pandoc-confluence-writer/master/confluence.lua"

UPDATE_CONFLUENCE_FILTER = [
    "wget", "-N", CONFLUENCE_FILTER_URL]

MD_EXTENSION = '.md'
MD_HEADER_START = '# '

IMG_TAG_START = '<ac:image><ri:attachment ri:filename="'
IMG_TAG_END = '" /></ac:image>'

GITBOOK_TAG_BEGIN = '{%'
GITBOOK_TAG_END = '%}'

SVG_EXTENSION = ".svg"
SVG_W_START = 'width="'
SVG_W_END = 'px"'
SVG_H_START = 'height="'
SVG_H_END = 'px"'
SVG_VIEWBOX_TAG = 'viewBox="'

SVG_MAX_WIDTH = 1000
SVG_MAX_HEIGHT = 1500

CONFLUENCE_TAG_AC_STYLE_BEGIN = '<ac:structured-macro ac:macro-id="'
CONFLUENCE_TAG_AC_STYLE_END = '</style>]]></ac:plain-text-body></ac:structured-macro>'
CONFLUENCE_TAG_AC_IMAGE_BEGIN = '<ac:image>'
CONFLUENCE_TAG_AC_IMAGE_END = '</ac:image>'


import os
import sys
import numpy as np
from atlassian import Confluence

CONFLUENCE_FILTER_NAME = 'confluence.lua'
CONFLUENCE_FILTER_URL = "https://raw.githubusercontent.com/jpbarrette/pandoc-confluence-writer/master/" + \
    CONFLUENCE_FILTER_NAME
UPDATE_CONFLUENCE_FILTER = "wget " + \
    CONFLUENCE_FILTER_URL + " -O " + CONFLUENCE_FILTER_NAME

MD_FOLDER = "./engineering-standards"
MD_EXTENSION = '.md'
CONFLUENCE_EXTENSION = '.cf'
SVG_EXTENSION = ".svg"

TMP_FILE = "_filetemp.tmp"

IMG_TAG_START = '<ac:image><ri:attachment ri:filename="'
IMG_TAG_END = '" /></ac:image>'
IMG_SRC_TAG_END = '" data-origin=".'

HTML_STYLE_BEGIN = '<style>'
HTML_STYLE_END = '</style>'

OS_COMMAND_LIST_FILES = "find " + MD_FOLDER + " -name '*" + \
    MD_EXTENSION + "' | sort -fr >> " + TMP_FILE

OS_COMMAND_LIST_CFL_FILES = "find " + MD_FOLDER + " -name '*" + \
    CONFLUENCE_EXTENSION + "' | sort -fr >> " + TMP_FILE

CONFLUENCE_SPACE = '~613673678'
CONFLUENCE_URL = 'https://vibrato.atlassian.net'
CONFLUENCE_USERID = 'konstantin.vanyushov@servian.com'
CONFLUENCE_OATOKEN = 'ozL4ruBp6vyjIKpj14la749B'
CONFLUENCE_ROOT_PAGE_NAME = MD_FOLDER.replace('./', '')

confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERID,
    password=CONFLUENCE_OATOKEN)

root_page_id = ''
confluence_parent_id_index = ''


def main():

    try:
        update_confluence_filter()
        # delete_root_page()    # Think twice before using this!
        create_root_page()
        convert_markdown_to_confluence()
        build_confluence_document_tree()
        # push_to_confluence()
        filesystem_cleanup()
    except:
        filesystem_cleanup()
        print("Unexpected error:", sys.exc_info()[0])
        raise


def build_confluence_document_tree():
    global confluence_parent_id_index
    print(confluence_parent_id_index)
    for item in confluence_parent_id_index:
        update_empty_confluence_page(item[0], item[1])


def create_root_page():
    global root_page_id
    root_page_id = get_confluence_page_id(CONFLUENCE_ROOT_PAGE_NAME)

    if confluence.page_exists(space=CONFLUENCE_SPACE, title=CONFLUENCE_ROOT_PAGE_NAME):
        confluence.remove_page(
            root_page_id,
            status=None,
            recursive=True)

    create_empty_confluence_page(CONFLUENCE_ROOT_PAGE_NAME)

    root_page_id = get_confluence_page_id(CONFLUENCE_ROOT_PAGE_NAME)


def delete_root_page():
    global root_page_id
    root_page_id = get_confluence_page_id(CONFLUENCE_ROOT_PAGE_NAME)
    confluence.remove_page(
        root_page_id,
        status=None,
        recursive=True)


def get_confluence_page_id(title):
    return(confluence.get_page_id(
        space=CONFLUENCE_SPACE,
        title=title))


def create_empty_confluence_page(title):
    return(confluence.create_page(
        space=CONFLUENCE_SPACE,
        title=title,
        body=''))


def update_empty_confluence_page(title, parent_id):
    return (confluence.update_or_create(
        parent_id=parent_id,
        title=title,
        body='',
        representation='storage'))


def convert_markdown_to_confluence():
    os.system(OS_COMMAND_LIST_FILES)
    md_files_list = open(TMP_FILE)

    create_confluence_document_tree(md_files_list)

    for md_file in md_files_list:
        convert_md_file(md_file)

    md_files_list.close()
    os.system('rm ' + TMP_FILE)


def create_confluence_document_tree(md_files_list):
    confluence_index = []
    global confluence_parent_id_index
    global root_page_id

    for md_file in md_files_list:
        filesystem_path_items = (md_file.replace('./', '').replace('\n',
                                                                   '').replace(MD_EXTENSION, '').split('/'))

        i = 0
        for filesystem_item in filesystem_path_items:
            if i == 0:
                parent_id = CONFLUENCE_SPACE
                title = CONFLUENCE_ROOT_PAGE_NAME
            if i == 1:
                title = filesystem_item
                parent_id = root_page_id
            if i > 1:
                title = filesystem_item
                parent_id = get_confluence_page_id(
                    filesystem_path_items[i - 1])
            if i > 0:
                update_empty_confluence_page(title, parent_id)
            confluence_index.append([title, parent_id])
            i += 1
    confluence_parent_id_index = np.unique(np.array(confluence_index), axis=0)


def update_confluence_filter():
    os.system(UPDATE_CONFLUENCE_FILTER)


def convert_md_file(md_file):
    with open(md_file) as fp:
        temp_file_name = md_file + CONFLUENCE_EXTENSION
        temp_file = open(temp_file_name, "w+")
        PANDOC_OS_COMMAND = 'pandoc -t ' + CONFLUENCE_FILTER_NAME + \
            ' ' + md_file + ' >> ' + temp_file_name
        os.system(PANDOC_OS_COMMAND)
        temp_file.close()


def push_confluence_file(cfl_file):

    with open(cfl_file) as fp:
        cfl_content = fp.read()

        title = find_confluence_title(cfl_content)

        svg_image = find_svg_image_link(cfl_content)
        svg_file_name = find_svg_image_filename(svg_image)

        cfl_content = cleanup_html_style(cfl_content)
        cfl_content = cfl_content.replace(svg_image, svg_file_name)

        status = confluence.create_page(
            space=CONFLUENCE_SPACE,
            title=title,
            body='',
            parent_id=parent_id)

        if svg_image:
            svg_image_path = MD_FOLDER + "/" + str(svg_image)
            upload_file_as_an_attachment(
                svg_image_path, svg_file_name, title)

        status = confluence.update_or_create(
            parent_id=parent_id,
            title=title,
            body=cfl_content)


def upload_file_as_an_attachment(svg_image, svg_file_name, title):
    svg_file = open(svg_image)
    status = confluence.attach_content(
        svg_file.read(),
        name=(svg_file_name),
        content_type='image',
        page_id=None,
        title=title,
        space=None,
        comment=None)
    svg_file.close()


def find_svg_image_link(content):
    begin = content.find(IMG_TAG_START)
    end = content.find(IMG_TAG_END)
    path = content[begin:end].replace(IMG_TAG_START, "").replace(
        "./../.", "").replace("./.", "")
    return(path)


def find_svg_image_filename(link):
    begin = link.rfind("/") + 1
    return(link[begin:])


def cleanup_html_style(content):
    begin = content.find(HTML_STYLE_BEGIN)
    end = content.find(HTML_STYLE_END)
    content = content.replace((content[begin:end] + HTML_STYLE_END), '')
    return (content)


def find_confluence_title(content):
    CONFLUENCE_NAME_TAG_BEGIN = '<ac:parameter ac:name="">'
    begin = content.find(CONFLUENCE_NAME_TAG_BEGIN)
    CONFLUENCE_NAME_TAG_END = '</ac:parameter>'
    end = content.find(CONFLUENCE_NAME_TAG_END, begin)
    title = content[begin:end].replace(CONFLUENCE_NAME_TAG_BEGIN, '')
    return(title)


def push_to_confluence():
    os.system(OS_COMMAND_LIST_CFL_FILES)
    cfl_files_list = open(TMP_FILE)
    for cfl_file in cfl_files_list:
        push_confluence_file(cfl_file)

    cfl_files_list.close()


def filesystem_cleanup():
    os.system('rm ' + TMP_FILE)
    os.system('rm **/*.cf')


main()

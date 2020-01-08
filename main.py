
import os
import sys
from atlassian import Confluence
from progress.bar import Bar

CONFLUENCE_FILTER_NAME = 'confluence.lua'
CONFLUENCE_FILTER_URL = "https://raw.githubusercontent.com/jpbarrette/pandoc-confluence-writer/master/" + \
    CONFLUENCE_FILTER_NAME
UPDATE_CONFLUENCE_FILTER = "wget " + \
    CONFLUENCE_FILTER_URL + " -O " + CONFLUENCE_FILTER_NAME

MD_FOLDER = "./engineering-standards"
MD_EXTENSION = '.md'
CONFLUENCE_EXTENSION = '.cf'

TMP_FILE = "_filetemp.tmp"

IMG_TAG_START = '<ac:image><ri:attachment ri:filename="'
IMG_TAG_END = '" /></ac:image>'

HTML_STYLE_BEGIN = '<style>'
HTML_STYLE_END = '</style>'

MD_HEADER_START = '# '

OS_COMMAND_LIST_FILES = "find " + MD_FOLDER + " -name '*" + \
    MD_EXTENSION + "' | sort -fr >> " + TMP_FILE

CONFLUENCE_SPACE = '~613673678'
CONFLUENCE_URL = 'https://vibrato.atlassian.net'
CONFLUENCE_USERID = 'konstantin.vanyushov@servian.com'
CONFLUENCE_OATOKEN = 'ozL4ruBp6vyjIKpj14la749B'
CONFLUENCE_ROOT_PAGE_NAME = MD_FOLDER.replace('./', '')
CONFLUENCE_SECTION_CONTENT_FILE = "README.md"
CONFLUENCE_TABLE_OF_CONTENTS = "SUMMARY.md"

confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERID,
    password=CONFLUENCE_OATOKEN)

root_page_id = ''
confluence_parent_id_index = ''


def main():

    try:
        bar = Bar('Processing', max=6)
        filesystem_cleanup()
        update_confluence_filter()
        bar.next()
        # Think twice before using this as it will delete the main document tree and all the contents!
        delete_root_page()
        bar.next()
        create_root_page()
        bar.next()
        convert_files_and_create_confluence_document_tree()
        bar.next()
        publish_content_to_confluence()
        bar.next()
        filesystem_cleanup()
        bar.next()
    except:
        filesystem_cleanup()
        print("Unexpected error:", sys.exc_info()[0])
        raise


def create_root_page():
    global root_page_id
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
        body=""))


def update_empty_confluence_page(name, parent_id):
    return (confluence.update_or_create(
        parent_id=parent_id,
        title=name,
        body='',
        representation="storage"))


def convert_files_and_create_confluence_document_tree():
    os.system(OS_COMMAND_LIST_FILES)
    md_files_list = open(TMP_FILE)
    create_confluence_document_tree(md_files_list)
    md_files_list.close()

    convert_md_files()


def create_confluence_document_tree(md_files_list):
    confluence_index = []
    global confluence_parent_id_index
    global root_page_id

    for md_file in md_files_list:

        md_file = md_file.replace('\n', '')

        if md_file.endswith(CONFLUENCE_TABLE_OF_CONTENTS) is not True:

            filesystem_path_items = (md_file.replace(
                './', '').replace(MD_EXTENSION, '').split('/'))

            path_index = 0
            for filesystem_item in filesystem_path_items:

                file = open(md_file)
                if filesystem_item == filesystem_path_items[-1]:
                    title = find_markdown_title(file)
                    file.seek(0)
                else:
                    title = filesystem_item
                file.close()

                if path_index == 0:
                    parent_id = CONFLUENCE_SPACE
                    title = CONFLUENCE_ROOT_PAGE_NAME
                    page_id = root_page_id
                if path_index == 1:
                    parent_id = root_page_id
                if path_index > 1:
                    parent_id = page_id
                    # parent_id = get_confluence_page_id(
                    # filesystem_path_items[path_index - 1])
                if path_index > 0:
                    if md_file.endswith(CONFLUENCE_SECTION_CONTENT_FILE) is not True:
                        # status = update_empty_confluence_page(title, parent_id)
                        status = update_empty_confluence_page(
                            filesystem_item, parent_id)
                        page_id = status['id']
                    else:
                        page_id = parent_id
                    confluence_index.append(
                        [md_file, filesystem_item, title, parent_id, page_id])
                path_index += 1

    confluence_parent_id_index = confluence_index


def update_confluence_filter():
    os.system(UPDATE_CONFLUENCE_FILTER)


def convert_md_files():
    global confluence_parent_id_index
    for md_file in confluence_parent_id_index:
        temp_file_name = md_file[0] + CONFLUENCE_EXTENSION
        PANDOC_OS_COMMAND = 'pandoc -t ' + CONFLUENCE_FILTER_NAME + \
            ' ' + md_file[0] + ' > ' + temp_file_name
        os.system(PANDOC_OS_COMMAND)


def upload_file_as_an_attachment(svg_image, svg_file_name, title, page_id):
    svg_file = open(svg_image)
    status = confluence.attach_content(
        svg_file.read(),
        name=(svg_file_name),
        content_type='image',
        page_id=page_id,
        title=title,
        space=None,
        comment=None)
    svg_file.close()


def find_svg_image_link(content):
    begin = content.find(IMG_TAG_START)
    end = content.find(IMG_TAG_END)
    path = content[begin:end].replace(IMG_TAG_START, "")
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


def find_markdown_title(file):
    title = ''
    for line in file:
        if line.strip().startswith(MD_HEADER_START):
            title = line.replace(MD_HEADER_START, '')
            title = title.replace('\n', '')
    return(title)


def publish_content_to_confluence():
    global confluence_parent_id_index
    path_index = 0
    for file_record in confluence_parent_id_index:
        cfl_file_path = file_record[0] + CONFLUENCE_EXTENSION

        with open(cfl_file_path) as fp:
            cfl_content = fp.read()

            # title = cfl_file_path.replace(MD_EXTENSION, '').replace(
            #     CONFLUENCE_EXTENSION, '')

            # title = find_confluence_title(cfl_content)
            title = file_record[2]

            svg_image = find_svg_image_link(cfl_content)
            if svg_image:
                svg_file_name = find_svg_image_filename(svg_image)
                svg_image_path = MD_FOLDER + "/" + \
                    str(svg_image).replace("./../.", "").replace("./.", "")
                cfl_content = cfl_content.replace(svg_image, svg_file_name)
                upload_file_as_an_attachment(
                    svg_image_path, svg_file_name, title, file_record[4])

            cfl_content = cleanup_html_style(cfl_content)

            if file_record[0].endswith(CONFLUENCE_SECTION_CONTENT_FILE):
                page_id = file_record[3]
            else:
                page_id = file_record[4]

            confluence.update_page(
                page_id=page_id,
                title=file_record[2],
                body=cfl_content,
                parent_id=file_record[3],
                type='page',
                representation='storage',
                minor_edit=False)

        path_index += 1


def filesystem_cleanup():
    os.system('rm *.tmp')
    os.system(('rm **/*' + CONFLUENCE_EXTENSION))


main()


import os
import re
import sys

from atlassian import Confluence

# from progress.bar import Bar

CONFLUENCE_FILTER_NAME = 'confluence.lua'
CONFLUENCE_FILTER_URL = \
    "https://raw.githubusercontent.com/jpbarrette/pandoc-confluence-writer/master/" + \
    CONFLUENCE_FILTER_NAME
UPDATE_CONFLUENCE_FILTER = "wget " + \
    CONFLUENCE_FILTER_URL + " -O " + CONFLUENCE_FILTER_NAME

CONFLUENCE_EXTENSION = '.cf'
TMP_FILE = "_filetemp.tmp"

MD_EXTENSION = '.md'
MD_HEADER_START = '# '

IMG_TAG_START = '<ac:image><ri:attachment ri:filename="'
IMG_TAG_END = '" /></ac:image>'

SVG_EXTENSION = ".svg"
SVG_W_START = 'width="'
SVG_W_END = 'px"'
SVG_H_START = 'height="'
SVG_H_END = 'px"'

SVG_MAX_WIDTH = 1000

AC_STYLE_BEGIN = '<ac:structured-macro ac:macro-id="'
AC_STYLE_END = '</style>]]></ac:plain-text-body></ac:structured-macro>'
AC_DIV_BEGIN = '<ac:structured-macro ac:macro-id='
AC_DIV_END = '</ac:structured-macro>'
AC_IMAGE_BEGIN = '<ac:image>'
AC_IMAGE_END = '</ac:image>'
AC_IMAGE_BEGIN_WIDTH_1000 = '<ac:image ac:align="center" ac:width="' + \
    str(SVG_MAX_WIDTH) + '">'

SOURCE_FOLDER = "./engineering-standards"
CONFLUENCE_SPACE = '~613673678'
CONFLUENCE_URL = 'https://vibrato.atlassian.net'
CONFLUENCE_USERID = 'konstantin.vanyushov@servian.com'
CONFLUENCE_OATOKEN = 'ozL4ruBp6vyjIKpj14la749B'
CONFLUENCE_ROOT_PAGE_NAME = SOURCE_FOLDER.replace('./', '')
CONFLUENCE_SECTION_CONTENT_FILE = "README.md"
CONFLUENCE_TABLE_OF_CONTENTS = "SUMMARY.md"

OS_COMMAND_LIST_FILES = "find " + SOURCE_FOLDER + " -name '*" + \
    MD_EXTENSION + "' | sort -fr >> " + TMP_FILE

confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERID,
    password=CONFLUENCE_OATOKEN)

root_page_id = ''
confluence_parent_id_index = ''


def main():

    try:
        filesystem_cleanup()
        # update_confluence_filter()
        # Think twice before using this as it will delete the main document
        # tree and all the contents!
        delete_root_page()
        create_root_page()
        convert_files_and_create_confluence_document_tree()
        publish_content_to_confluence()
        filesystem_cleanup()
    except:
        filesystem_cleanup()
        print("Unexpected error:", sys.exc_info()[0])
        raise


def filesystem_cleanup():
    # for root, dirs, files in os.walk(SOURCE_FOLDER):
    #     print(root)
    #     print(dirs)
    #     print(files)
    # os.remove('./' + TMP_FILE)
    os.system('rm *.tmp')
    os.system(('rm **/*' + CONFLUENCE_EXTENSION))


def update_confluence_filter():
    os.system(UPDATE_CONFLUENCE_FILTER)


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
                if path_index > 0:
                    if md_file.endswith(CONFLUENCE_SECTION_CONTENT_FILE) is not True:
                        status = update_empty_confluence_page(title, parent_id)
                        page_id = status['id']
                    else:
                        page_id = parent_id
                    confluence_index.append(
                        [md_file, filesystem_item, title, parent_id, page_id])
                path_index += 1

    confluence_parent_id_index = confluence_index


def convert_md_files():
    global confluence_parent_id_index
    for md_file in confluence_parent_id_index:
        temp_file_name = md_file[0] + CONFLUENCE_EXTENSION
        PANDOC_OS_COMMAND = 'pandoc -t ' + CONFLUENCE_FILTER_NAME + \
            ' ' + md_file[0] + ' > ' + temp_file_name
        os.system(PANDOC_OS_COMMAND)


def find_svg_image_filename(link):
    begin = link.rfind("/") + 1
    return(link[begin:])


def find_svg_image_link(content):
    path = []
    img_tag_begin_positions = [(entry.end()) for entry in list(
        re.finditer(IMG_TAG_START, content))]
    img_tag_end_positions = [(entry.start()) for entry in list(
        re.finditer(IMG_TAG_END, content))]
    index = 0
    for begin in img_tag_begin_positions:
        end = img_tag_end_positions[index]
        img_path = content[begin:end].replace(
            IMG_TAG_START, "")
        if img_path:
            path.append(img_path)
        index += 1
    return(path)


def find_svg_image_dimensions(svg_image_path):
    size = []
    svg_file = open(svg_image_path)
    content = svg_file.read()
    width_tag_begin_position = content.find(SVG_W_START)
    width_tag_end_position = content.find(SVG_W_END, width_tag_begin_position)
    width = content[(width_tag_begin_position + len(SVG_W_START))
                     :width_tag_end_position]
    height_tag_begin_position = content.find(
        SVG_H_START, width_tag_end_position)
    height_tag_end_position = content.find(
        SVG_H_END, height_tag_begin_position)
    height = content[(height_tag_begin_position +
                      len(SVG_H_START)):height_tag_end_position]
    svg_file.close()
    size = [int(width), int(height)]
    return(size)


def upload_svg_file_to_confluence_as_an_attachment(
        svg_image_path,
        svg_file_name,
        title, page_id,
        size_override,
        svg_size,
        svg_size_new):

    svg_file = open(svg_image_path)
    svg_file_content = svg_file.read()
    svg_file.close()

    if size_override:
        WIDTH_TAG = 'width="'
        HEIGHT_TAG = 'height="'
        old_width = WIDTH_TAG + str(svg_size[0])
        old_height = HEIGHT_TAG + str(svg_size[1])
        new_width = WIDTH_TAG + str(svg_size_new[0])
        new_height = HEIGHT_TAG + str(svg_size_new[1])
        svg_file_content.replace(old_width, new_width)
        svg_file_content.replace(old_height, new_height)

        print(old_width, old_height, new_width, new_height)

    confluence.attach_content(
        svg_file_content,
        name=svg_file_name,
        content_type='image',
        page_id=page_id,
        title=title,
        space=None,
        comment=None)


def cleanup_confluence_html(content):
    # def cleanup(content, start, stop, add):
    #     begin = content.find(start)
    #     end = content.find(stop)
    #     return(content.replace((content[begin:end] + add), ''))
    # content = cleanup(content, AC_STYLE_BEGIN, AC_STYLE_END, AC_STYLE_END)
    # content = cleanup(content, AC_DIV_BEGIN, AC_IMAGE_BEGIN, '')
    # content = cleanup(content, AC_IMAGE_END, AC_DIV_END, '')

    begin = content.find(AC_STYLE_BEGIN)
    end = content.find(AC_STYLE_END)
    content = content.replace((content[begin:end] + AC_STYLE_END), '')
    # begin = content.find(AC_DIV_BEGIN)
    # end = content.find(AC_IMAGE_BEGIN)
    # content = content.replace(content[begin:end], '')
    # begin = content.find(AC_IMAGE_END)
    # end = content.find(AC_DIV_END)
    # content = content.replace(content[begin:end], '')
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

        # title = find_confluence_title(cfl_content)
        title = file_record[2]
        parent_id = file_record[3]
        page_id = file_record[4]

        with open(cfl_file_path) as fp:
            confluence_file_content = fp.read()

            svg_images = find_svg_image_link(confluence_file_content)

            for svg_image_path in svg_images:

                SVG_SIZE_OVERRIDE = False
                svg_size_new = []

                if svg_image_path and svg_image_path.endswith(SVG_EXTENSION):
                    svg_file_name = find_svg_image_filename(svg_image_path)
                    # png_file_name = svg_file_name.replace('.svg', '.png')
                    confluence_file_content = confluence_file_content.replace(
                        svg_image_path, svg_file_name)
                    if svg_image_path.startswith('../../'):
                        svg_image_path = svg_image_path.replace(
                            '../..', SOURCE_FOLDER)
                    else:
                        svg_image_path = SOURCE_FOLDER + "/" + \
                            svg_image_path.replace('../', '')

                    svg_size = find_svg_image_dimensions(svg_image_path)
                    if svg_size:
                        if int(svg_size[0]) > SVG_MAX_WIDTH:
                            SVG_SIZE_OVERRIDE = True
                            svg_aspect_ratio = (svg_size[0] / svg_size[1])
                            svg_new_height = int(
                                (SVG_MAX_WIDTH / svg_aspect_ratio))
                            svg_size_new = [SVG_MAX_WIDTH, svg_new_height]
                            # confluence_file_content = confluence_file_content.replace(
                            #     AC_IMAGE_BEGIN, AC_IMAGE_BEGIN_WIDTH_1000)
                    upload_svg_file_to_confluence_as_an_attachment(
                        svg_image_path,
                        svg_file_name,
                        title, page_id,
                        SVG_SIZE_OVERRIDE,
                        svg_size,
                        svg_size_new)

            confluence_file_content = cleanup_confluence_html(
                confluence_file_content)
            # print(confluence_file_content)
            # if file_record[0].endswith(CONFLUENCE_SECTION_CONTENT_FILE):
            #     # status = confluence.get_page_ancestors(page_id)
            #     # status = confluence.get_page_by_id(
            #     #     confluence, page_id, expand=None, status=None, version=None)
            #     # print(status)
            #     confluence.update_page(
            #         page_id=parent_id,
            #         title=title,
            #         body=confluence_file_content)
            # else:
            confluence.update_page(
                page_id=page_id,
                title=title,
                body=confluence_file_content,
                parent_id=parent_id,
                type='page',
                representation='storage',
                minor_edit=False)

        path_index += 1


def blockConsoleOutput():
    sys.stdout = open(os.devnull, 'w')


def enableConsoleOutput():
    sys.stdout = sys.__stdout__


main()

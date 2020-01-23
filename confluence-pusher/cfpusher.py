
from config import *
from atlassian import Confluence
import click
import json
import os
import re
import subprocess
import sys
from subprocess import PIPE, STDOUT, Popen
import glob

try:
    file = open("config.json")
    if file:
        config_file = file.read()
        file.close()
        configuration = json.loads(config_file)
        CONFLUENCE_SPACE = configuration['CONFLUENCE_SPACE']
        CONFLUENCE_URL = configuration['CONFLUENCE_URL']
        CONFLUENCE_USERID = configuration['CONFLUENCE_USERID']
        CONFLUENCE_OATOKEN = configuration['CONFLUENCE_OATOKEN']
        DELETE_ROOT_DOCUMENT_ON_STARTUP = configuration['DELETE_ROOT_DOCUMENT_ON_STARTUP']
except OSError as err:
    print("Configuration file not found!")
    print("OS error: {0}".format(err))
    raise

confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERID,
    password=CONFLUENCE_OATOKEN)

root_page_id = ''
confluence_documents_index = ''
file_list = []

CONFLUENCE_ROOT_PAGE_NAME = ''


@click.command()
@click.option('-s', '--source-folder', 'sourcefolder', required=True, type=str)
def cfpusher(sourcefolder):
    global root_page_id
    global SOURCE_FOLDER
    global CONFLUENCE_ROOT_PAGE_NAME
    SOURCE_FOLDER = sourcefolder

    CONFLUENCE_ROOT_PAGE_NAME = SOURCE_FOLDER.split('/')[-1].replace('\n', '')

    try:
        check_if_configured()
        # update_confluence_filter()
        delete_root_page_if_configured()
        create_root_page_if_not_exist()
        convert_files_and_create_confluence_document_tree()
        publish_content_to_confluence()
    except KeyError:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    except OSError as err:
        print("OS error: {0}".format(err))
        raise
    except ValueError as err:
        print(err)
    finally:
        print("Stopped.")


def check_if_configured():
    if CONFLUENCE_URL == '' or CONFLUENCE_USERID == '' or CONFLUENCE_OATOKEN == '':
        raise ValueError(
            'Please make sure that the following configuration parameters are configured in config.py:\nCONFLUENCE_URL\nCONFLUENCE_USERID\nCONFLUENCE_OATOKEN')


def update_confluence_filter():
    print('###   Updating confluence.lua filter   ###')
    subprocess.call(UPDATE_CONFLUENCE_FILTER)


def delete_root_page_if_configured():
    global root_page_id
    global DELETE_ROOT_DOCUMENT_ON_STARTUP
    if DELETE_ROOT_DOCUMENT_ON_STARTUP == True:
        print('###   Deleting root page of the document   ###')
        root_page_id = get_confluence_page_id(CONFLUENCE_ROOT_PAGE_NAME)
        confluence.remove_page(
            root_page_id,
            status=None,
            recursive=True)


def create_root_page_if_not_exist():
    global root_page_id
    if confluence.page_exists(CONFLUENCE_SPACE, CONFLUENCE_ROOT_PAGE_NAME) == False:
        print('###   Creating root page of the document   ###')
        create_empty_confluence_page(CONFLUENCE_ROOT_PAGE_NAME)
        root_page_id = get_confluence_page_id(CONFLUENCE_ROOT_PAGE_NAME)
        print(root_page_id)


def convert_files_and_create_confluence_document_tree():
    global confluence_documents_index
    global root_page_id
    global file_list

    print('###   Creating confluence document tree   ###')

    mask = SOURCE_FOLDER + '/**/*' + MD_EXTENSION
    for files in glob.glob(mask, recursive=True):
        if files.endswith(CONFLUENCE_TABLE_OF_CONTENTS) == False:
            file_record = files.replace(
                (SOURCE_FOLDER + '/'), '').replace('\n', '').split('/')
            index = 0
            for item in file_record:
                if item.endswith(CONFLUENCE_SECTION_CONTENT_FILE) == False:
                    if index == 0 and item.endswith(MD_EXTENSION):
                        title = find_markdown_title(files)
                        update_empty_confluence_page(title, root_page_id)
                    if index == 0 and item.endswith(MD_EXTENSION) == False:
                        title = item
                        update_empty_confluence_page(title, root_page_id)
                    if index > 0 and item.endswith(MD_EXTENSION):
                        title = find_markdown_title(files)
                        parent_id = get_confluence_page_id(
                            (file_record[index-1]))
                        update_empty_confluence_page(title, parent_id)
                    if index > 0 and item.endswith(MD_EXTENSION) == False:
                        title = item
                        parent_id = get_confluence_page_id(
                            (file_record[index-1]))
                        update_empty_confluence_page(title, parent_id)
                index += 1
            file_list.append(files)


def pandoc_conversion(file_name):
    md_file = open(file_name)
    file_contents = md_file.read()
    md_file.close()

    file_contents = cleanup_markdown_before_conversion(
        file_contents, GITBOOK_TAG_BEGIN, GITBOOK_TAG_END)

    file_contents = file_contents.encode('UTF-8')
    PANDOC_COMMAND = ['pandoc', '-t',
                      CONFLUENCE_FILTER_NAME]
    pandoc = subprocess.Popen(PANDOC_COMMAND, stdout=PIPE,
                              stdin=PIPE, stderr=STDOUT)
    confluence_content = pandoc.communicate(input=file_contents)
    return(confluence_content[0].decode('UTF-8'))


def cleanup_markdown_before_conversion(content, start_tag, end_tag):
    gitbook_content_to_remove = []
    tag_begin_positions = [(entry.end()) for entry in list(
        re.finditer(start_tag, content))]
    tag_end_positions = [(entry.start()) for entry in list(
        re.finditer(end_tag, content))]
    index = 0
    for begin in tag_begin_positions:
        end = tag_end_positions[index]
        gitbook_content_to_remove.append(
            start_tag + content[begin:end] + end_tag)
        index += 1
    for entry in gitbook_content_to_remove:
        content = content.replace(entry, '')
    return (content)


def find_markdown_title(file_name):
    title = ''
    file = open(file_name)
    for line in file:
        if line.strip().startswith(MD_HEADER_START):
            title = line.replace(MD_HEADER_START, '')
            title = title.replace('\n', '')
    file.close()
    return(title)


def publish_content_to_confluence():
    global confluence_documents_index
    global root_page_id
    global file_list

    print('###   Publishing content to Confluence tree   ###')

    for file_record in file_list:
        if file_record.endswith(CONFLUENCE_SECTION_CONTENT_FILE) == True:
            title = file_record.split('/')[-2]
            page_id = get_confluence_page_id(title)
        else:
            title = find_markdown_title(file_record)
            page_id = get_confluence_page_id(title)

        confluence_file_content = pandoc_conversion(file_record)

        svg_images = find_svg_image_link(
            confluence_file_content, IMG_TAG_START, IMG_TAG_END)

        for svg_image_path in svg_images:
            confluence_file_content = resize_and_upload_svg_image(
                svg_image_path, confluence_file_content, page_id)

        confluence_file_content = confluence_file_content.replace(
            '../..', SOURCE_FOLDER)

        confluence_file_content = cleanup_confluence_html(
            confluence_file_content)

        confluence.append_page(
            page_id=page_id,
            title=title,
            append_body=confluence_file_content)
    print('Completed successfully.')


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
        representation='storage'))


def check_and_update_svg_image_dimensions(svg_image_path):

    size = []

    svg_file = open(svg_image_path)
    svg_file_content = svg_file.read()
    svg_file.close()

    width_tag_begin_position = svg_file_content.find(SVG_W_START)
    width_tag_end_position = svg_file_content.find(
        SVG_W_END, width_tag_begin_position)
    width_tag_begin_position += len(SVG_W_START)
    width = svg_file_content[width_tag_begin_position:width_tag_end_position]

    height_tag_begin_position = svg_file_content.find(
        SVG_H_START, width_tag_end_position)
    height_tag_end_position = svg_file_content.find(
        SVG_H_END, height_tag_begin_position)
    height = svg_file_content[(height_tag_begin_position +
                               len(SVG_H_START)):height_tag_end_position]

    size = [int(width), int(height)]
    return(size)


def upload_svg_file_to_confluence_as_an_attachment(
        svg_image_path,
        svg_file_name,
        title,
        page_id,
        width_override,
        height_override,
        svg_size,
        svg_size_new):

    SVG_VIEWBOX_CLOSING_TAG = '" '
    old_svg_viewbox_tag = ''
    new_svg_viewbox_tag = ''

    svg_file = open(svg_image_path)
    svg_file_content = svg_file.read()
    svg_file.close()

    if width_override or height_override:
        old_width = SVG_W_START + str(svg_size[0]) + SVG_W_END
        old_height = SVG_H_START + str(svg_size[1]) + SVG_H_END
        new_width = SVG_W_START + str(svg_size_new[0]) + SVG_W_END
        new_height = SVG_H_START + str(svg_size_new[1]) + SVG_H_END

        if width_override:
            new_height = SVG_H_START + 'auto"'
        if height_override:
            new_width = SVG_W_START + 'auto"'

        svg_file_content = svg_file_content.replace(
            old_width, new_width).replace(old_height, new_height)

        svg_viewbox_start = svg_file_content.find(SVG_VIEWBOX_TAG)
        svg_viewbox_end = svg_file_content.find(
            SVG_VIEWBOX_CLOSING_TAG, (svg_viewbox_start + len(SVG_W_START)))

        old_svg_viewbox_tag = (
            svg_file_content[svg_viewbox_start:svg_viewbox_end]
            + SVG_VIEWBOX_CLOSING_TAG)

        new_svg_viewbox_tag = old_svg_viewbox_tag + ' preserveAspectRatio="none" '

        svg_file_content = svg_file_content.replace(
            old_svg_viewbox_tag, new_svg_viewbox_tag)

    confluence.attach_content(
        content=svg_file_content,
        name=svg_file_name,
        content_type='image',
        page_id=page_id,
        title=title,
        space=None,
        comment=None)


def resize_and_upload_svg_image(svg_image_path, confluence_file_content, page_id):
    SVG_WIDTH_OVERRIDE = False
    SVG_HEIGHT_OVERRIDE = False

    status = confluence.get_page_by_id(page_id)
    title = status['title']

    svg_size_new = []

    if svg_image_path and svg_image_path.endswith(SVG_EXTENSION):
        svg_file_name = find_svg_image_filename(svg_image_path)
        confluence_file_content = confluence_file_content.replace(
            svg_image_path, svg_file_name)
        if svg_image_path.startswith('../../'):
            svg_image_path = svg_image_path.replace(
                '../..', SOURCE_FOLDER)
        else:
            svg_image_path = SOURCE_FOLDER + "/" + \
                svg_image_path.replace('../', '')

        svg_size = check_and_update_svg_image_dimensions(svg_image_path)
        if svg_size:
            if int(svg_size[0]) > SVG_MAX_WIDTH and int(svg_size[0]) > int(svg_size[1]):
                SVG_WIDTH_OVERRIDE = True
                svg_aspect_ratio = (svg_size[0] / svg_size[1])
                svg_new_height = int(
                    (SVG_MAX_WIDTH / svg_aspect_ratio))
                svg_size_new = [SVG_MAX_WIDTH, svg_new_height]
            elif int(svg_size[1]) > SVG_MAX_HEIGHT:
                SVG_HEIGHT_OVERRIDE = True
                svg_aspect_ratio = (svg_size[1] / svg_size[0])
                svg_new_height = int(
                    (SVG_MAX_HEIGHT / svg_aspect_ratio))
                svg_size_new = [SVG_MAX_HEIGHT, svg_new_height]

        upload_svg_file_to_confluence_as_an_attachment(
            svg_image_path,
            svg_file_name,
            title,
            page_id,
            SVG_WIDTH_OVERRIDE,
            SVG_HEIGHT_OVERRIDE,
            svg_size,
            svg_size_new)
    return confluence_file_content


def find_svg_image_filename(link):
    begin = link.rfind("/") + 1
    return(link[begin:])


def find_svg_image_link(content, start_tag, end_tag):
    path = []
    img_tag_begin_positions = [(entry.end()) for entry in list(
        re.finditer(start_tag, content))]
    img_tag_end_positions = [(entry.start()) for entry in list(
        re.finditer(end_tag, content))]
    index = 0
    for begin in img_tag_begin_positions:
        end = img_tag_end_positions[index]
        img_path = content[begin:end].replace(
            start_tag, "")
        if img_path:
            path.append(img_path)
        index += 1
    return(path)


def cleanup_confluence_html(content):
    def content_cleanup(content, begin_tag, end_tag):
        begin = content.find(begin_tag)
        end = content.find(end_tag)
        content = content.replace(
            (content[begin:end] + end_tag), '')
        return (content)
    content = content_cleanup(
        content, CONFLUENCE_TAG_AC_STYLE_BEGIN, CONFLUENCE_TAG_AC_STYLE_END)
    return (content)


if __name__ == '__main__':
    cfpusher()

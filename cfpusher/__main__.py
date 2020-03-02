import sys, re, os, json, glob, click, subprocess
from subprocess import PIPE, STDOUT, Popen
from atlassian import Confluence

# CONSTANTS
SVG_MAX_WIDTH = 1000
SVG_MAX_HEIGHT = 1500
ROOT_FILE = "README.md"
SUMMARY_FILE = "SUMMARY.md"

ROOT_PAGE_ID = ''
ROOT_PAGE_NAME = ''
DOCUMENTS_INDEX = ''
FILE_LIST = []
SOURCE_FOLDER = ''
SPACE = ''
PARENT_PAGE_NAME = ''
OVERWRITE = False

@click.command()
@click.argument('--source-folder', required=False, type=str)
@click.argument('--url', required=True, type=str)
@click.argument('--user-id', required=True, type=str)
@click.argument('--oauth-token', required=True, type=str)
@click.argument('--space', required=True, type=str)
@click.argument('--parent-page', required=True, type=str)
@click.argument('--root-page', required=True, type=str)
@click.option('--overwrite', is_flag=True)
def main(source_folder, oauth_token, root_page, space, parent_page, url, user_id, overwrite=False):

    global SOURCE_FOLDER, ROOT_PAGE_NAME, PARENT_PAGE_NAME, OVERWRITE, SPACE
    if source_folder:
        SOURCE_FOLDER = source_folder
    else:
        SOURCE_FOLDER = os.getcwd()

    ROOT_PAGE_NAME = root_page
    PARENT_PAGE_NAME = parent_page
    OVERWRITE = overwrite
    SPACE = space
    confluence = Confluence(
        url = url,
        username = user_id,
        password = oauth_token)

    try:
        delete_root_page(confluence)
        create_root_page(confluence)
        convert_files_and_create_confluence_document_tree(confluence)
        publish_content_to_confluence(confluence)
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

def delete_root_page(confluence):
    global ROOT_PAGE_ID
    global OVERWRITE
    print(ROOT_PAGE_NAME)
    if OVERWRITE == True:
        print('###   Deleting root page of the document   ###')
        ROOT_PAGE_ID = get_confluence_page_id(
            confluence, ROOT_PAGE_NAME)
        print(ROOT_PAGE_ID)
        if ROOT_PAGE_ID:
            confluence.remove_page(
                ROOT_PAGE_ID,
                status=None,
                recursive=True)
        else:
            print('Root page does not exist.')

def create_root_page(confluence):
    global ROOT_PAGE_ID
    if confluence.page_exists(SPACE, ROOT_PAGE_NAME) == False:

        print('###   Creating root page of the document   ###')

        if PARENT_PAGE_NAME:
            confluence.create_page(
                space=SPACE,
                title=ROOT_PAGE_NAME,
                body="",
                parent_id=PARENT_PAGE_NAME)
        else:
            confluence.create_page(
                space=SPACE,
                title=ROOT_PAGE_NAME,
                body="")
        ROOT_PAGE_ID = get_confluence_page_id(
            confluence, ROOT_PAGE_NAME)
        print("Root page ID: ", ROOT_PAGE_ID)

def convert_files_and_create_confluence_document_tree(confluence):
    global DOCUMENTS_INDEX
    global ROOT_PAGE_ID
    global FILE_LIST

    print('###   Creating confluence document tree   ###')

    mask = SOURCE_FOLDER + '/**/*' + ".md"
    for files in glob.glob(mask, recursive=True):
        if files.endswith(SUMMARY_FILE) == False:
            file_record = files.replace(
                (SOURCE_FOLDER + '/'), '').replace('\n', '').split('/')
            index = 0
            for item in file_record:
                if item.endswith(ROOT_FILE) == False:
                    if index == 0 and item.endswith(".md"):
                        title = find_markdown_title(files)
                        update_empty_confluence_page(
                            confluence, title, ROOT_PAGE_ID)
                    if index == 0 and item.endswith(".md") == False:
                        title = item
                        update_empty_confluence_page(
                            confluence, title, ROOT_PAGE_ID)
                    if index > 0 and item.endswith(".md"):
                        title = find_markdown_title(files)
                        parent_id = get_confluence_page_id(confluence,
                                                           (file_record[index-1]))
                        update_empty_confluence_page(
                            confluence, title, parent_id)
                    if index > 0 and item.endswith(".md") == False:
                        title = item
                        parent_id = get_confluence_page_id(confluence,
                                                           (file_record[index-1]))
                        update_empty_confluence_page(
                            confluence, title, parent_id)
                index += 1
            FILE_LIST.append(files)

def pandoc_conversion(file_name):
    md_file = open(file_name)
    file_contents = md_file.read()
    md_file.close()

    file_contents = cleanup_markdown_before_conversion(
        file_contents, '{%', '%}')

    file_contents = cleanup_markdown_before_conversion(
        file_contents, "<!--", "-->")

    file_contents = file_contents.encode('UTF-8')
    PANDOC_COMMAND = ['pandoc', '-t',
                      'confluence.lua']
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
        if line.strip().startswith("# "):
            title = line.replace("# ", '')
            title = title.replace('\n', '')
    file.close()
    return(title)

def publish_content_to_confluence(confluence):
    global DOCUMENTS_INDEX
    global ROOT_PAGE_ID
    global FILE_LIST

    print('###   Publishing content to Confluence tree   ###')

    for file_record in FILE_LIST:
        if file_record.endswith(ROOT_FILE) == True:
            title = file_record.split('/')[-2]
            page_id = get_confluence_page_id(confluence, title)
        else:
            title = find_markdown_title(file_record)
            page_id = get_confluence_page_id(confluence, title)

        confluence_file_content = pandoc_conversion(file_record)

        svg_images = find_svg_image_link(
            confluence_file_content, '<ac:image><ri:attachment ri:filename="', '" /></ac:image>')

        for svg_image_path in svg_images:
            confluence_file_content = resize_and_upload_svg_image(confluence,
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

def get_confluence_page_id(confluence, title):
    return(confluence.get_page_id(
        space=SPACE,
        title=title))

def update_empty_confluence_page(confluence, name, parent_id):
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

    width_tag_begin_position = svg_file_content.find('width="')
    width_tag_end_position = svg_file_content.find(
        'px"', width_tag_begin_position)
    width_tag_begin_position += len('width="')
    width = svg_file_content[width_tag_begin_position:width_tag_end_position]

    height_tag_begin_position = svg_file_content.find(
        'height="', width_tag_end_position)
    height_tag_end_position = svg_file_content.find(
        'px"', height_tag_begin_position)
    height = svg_file_content[(height_tag_begin_position +
                               len('height="')):height_tag_end_position]

    size = [int(width), int(height)]
    return(size)

def upload_svg_file_to_confluence_as_an_attachment(
        confluence,
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
        old_width = 'width="' + str(svg_size[0]) + 'px"'
        old_height = 'height="' + str(svg_size[1]) + 'px"'
        new_width = 'width="' + str(svg_size_new[0]) + 'px"'
        new_height = 'height="' + str(svg_size_new[1]) + 'px"'

        if width_override:
            new_height = 'height="auto"'
        if height_override:
            new_width = 'width="auto"'

        svg_file_content = svg_file_content.replace(
            old_width, new_width).replace(old_height, new_height)

        svg_viewbox_start = svg_file_content.find('viewBox="')
        svg_viewbox_end = svg_file_content.find(
            SVG_VIEWBOX_CLOSING_TAG, (svg_viewbox_start + len('width="')))

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

def resize_and_upload_svg_image(confluence, svg_image_path, confluence_file_content, page_id):
    SVG_WIDTH_OVERRIDE = False
    SVG_HEIGHT_OVERRIDE = False

    status = confluence.get_page_by_id(page_id)
    title = status['title']

    svg_size_new = []

    if svg_image_path and svg_image_path.endswith('.svg'):
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
            confluence,
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
        content, '<ac:structured-macro ac:macro-id="', '</style>]]></ac:plain-text-body></ac:structured-macro>')
    return (content)

if __name__ == '__main__':
    main()

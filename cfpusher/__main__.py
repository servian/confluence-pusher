import sys, re, os, json, glob, click, subprocess
from subprocess import PIPE, STDOUT, Popen
from atlassian import Confluence

# CONSTANTS
SVG_MAX_WIDTH = 1000
SVG_MAX_HEIGHT = 1500
ROOT_FILE = "README.md"
SUMMARY_FILE = "SUMMARY.md"
SPACE = ''
CONF = ''
LUA = ''

@click.command()
@click.option('--url', required=True, type=str)
@click.option('--user-id', required=True, type=str)
@click.option('--oauth-token', required=True, type=str)
@click.option('--space', required=True, type=str)
@click.option('--parent-page', required=True, type=str)
@click.option('--overwrite', is_flag=True)
def main(oauth_token, space, parent_page, url, user_id, overwrite=True):

    global LUA, CONF, SPACE

    SPACE = space
    LUA = __file__.replace("__main__.py","confluence.lua")
    CONF = Confluence(url,user_id,oauth_token)
    parent = CONF.get_page_by_id(parent_page)
    if 'statusCode' in parent: raise Exception ("parent_page %s not found" % (parent_page))

    if overwrite:
        child_pages = CONF.get_child_pages(parent_page)
        for child_page in child_pages:
            CONF.remove_page(child_page['id'],recursive=True)

    source_folder = os.getcwd()
    create_page(source_folder, parent_page)

def create_page(path,parent_page):
    if os.path.isfile(path) and path.endswith(".md"):
        create_page_file(path, parent_page)

    elif os.path.isdir(path):

        this_file = os.path.join(path, ROOT_FILE)
        this_page_id = create_page_file(this_file, parent_page)
        child_paths = os.listdir(path)

        for child_path in child_paths:

            full_child_path = os.path.join(path,child_path)
            is_dir = os.path.isdir(full_child_path)
            is_md = os.path.basename(full_child_path).endswith(".md")

            if not full_child_path == this_file and (is_dir or is_md):
                create_page(full_child_path, this_page_id)
    else:
        raise Exception ("Specified path: %s is invalid to create a page from." % (path))

def create_page_file(path, parent_page):
    # Create Page based on explicit file
    title = get_markdown_header(path)
    if title == '':
        title = os.path.basename(path).replace(".md","")
    if not CONF.page_exists(SPACE, title):
        new_page = CONF.create_page(SPACE,title,'',parent_page)
    else: raise Exception ("Duplicate page with title %s in space %s" % (title, SPACE))
    if os.path.exists(path) and os.path.isfile(path) and os.path.basename(path).endswith(".md"):
        update_content(path,new_page['id'],title)
    return new_page['id']

def pandoc_conversion(file_name):
    md_file = open(file_name)
    file_contents = md_file.read()
    md_file.close()
    file_contents = re.sub(r"{%.*?%}","",file_contents,flags=re.DOTALL)
    file_contents = re.sub(r"<!--.*?-->","",file_contents,flags=re.DOTALL)
    file_contents = file_contents.encode('UTF-8')
    PANDOC_COMMAND = ['pandoc', '-t', LUA]
    pandoc = subprocess.Popen(PANDOC_COMMAND, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    confluence_content = pandoc.communicate(input=file_contents)
    return(confluence_content[0].decode('UTF-8'))

def get_markdown_header(path):
    title = ''
    if os.path.exists(path) and os.path.isfile(path) and os.path.basename(path).endswith(".md"):
        md_file = open(path)
        for line in md_file:
            if line.strip().startswith("# "):
                title = line.replace("# ", '')
                title = title.replace('\n', '')
                break
        md_file.close()
    return(title)

def update_content(path,page_id,title):

    content = pandoc_conversion(path)

    # GET ALL SVG IMAGE REFERENCES
    svg_regex = r"<ac:image><ri:attachment ri:filename=\"(.*?\.svg)\" /></ac:image>"
    svg_images = re.findall(svg_regex,content)

    # TEST TO SEE HOW THE IMAGE RELATIVE PATHS ARE HANDLED

    # UPLOAD ALL IMAGES
    for spath in svg_images:
        svg_content = resize_svg(os.path.join(os.path.dirname(path),spath),SVG_MAX_WIDTH,SVG_MAX_HEIGHT)
        file_name = os.path.basename(spath)
        CONF.attach_content(svg_content, file_name, 'image', page_id)

    # REMOVE RANDOM TAG
    macro_regex = r"(<ac:structured-macro.*?</ac:plain-text-body></ac:structured-macro>)"
    content = re.sub(macro_regex, "", content)

    CONF.update_page(page_id, title, content)

def resize_svg(path,w_constrain,h_constrain):

    if not (path and path.endswith('.svg')):
        raise Exception("Invalid file type.")
        
    svg_file = open(path)
    content = svg_file.read()
    svg_file.close()

    # Get current size
    w_regex = r"(width=\")(\d*)(px\")"
    width = (re.findall(w_regex, content))[0][1]
    h_regex = r"(height=\")(\d*)(px\")"
    height = (re.findall(h_regex, content))[0][1]

    new_width = int(width)
    new_height = int(height)

    if int(width) > int(height) and int(width) > w_constrain:
        ratio = int(width) / int(height)
        new_height = int(SVG_MAX_WIDTH / ratio)
        new_width = SVG_MAX_WIDTH
    elif int(height) > h_constrain:
        ratio = int(height) / int(width)
        new_width = int(SVG_MAX_HEIGHT / ratio)
        new_height = SVG_MAX_HEIGHT

    content = re.sub(w_regex, r'\g<1>' + str(new_width) + r'\g<3>', content, 1)
    content = re.sub(h_regex, r'\g<1>' + str(new_height) + r'\g<3>', content, 1)
    viewBox = "0 0 %s %s" % (width, height)
    vb_regex = r"(viewBox=\")([\-\.\d\s]*)(\")"
    content = re.sub(vb_regex, r'\g<1>' + viewBox + r'\g<3>', content, 1)

    return content

if __name__ == '__main__':
    main()
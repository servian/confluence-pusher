import os

HTML_FOLDER = "./html"
HTML_EXTENSION = '.html'
TMP_EXTENSION = '.tmp'
SVG_EXTENSION = ".svg"

IMG_TAG_START = '<img src="'
IMG_TAG_END = 'alt='
IMG_SRC_TAG_END = '" data-origin=".'

OS_COMMAND = "find " + HTML_FOLDER + " -name '*" + \
    HTML_EXTENSION + "' >> _filetemp.tmp"


def main():
    os.system(OS_COMMAND)
    html_files_list = open("_filetemp.tmp")

    for html_file in html_files_list:
        scan_html_files(html_file.strip())

    html_files_list.close()
    os.system('rm _filetemp.tmp')


def scan_html_files(html_file):
    with open(html_file) as fp:

        temp_file_name = html_file + TMP_EXTENSION
        temp_file = open(temp_file_name, "w+")

        for line_from_html_file in fp:
            scan_line_from_html_file(line_from_html_file, temp_file)

        temp_file.close()


def scan_line_from_html_file(line_from_html_file, temp_file):
    img_tag_position = line_from_html_file.find(IMG_TAG_START)
    if img_tag_position > -1:
        current_line = line_from_html_file.split(IMG_TAG_START)
        for item in current_line:
            line_position_end = line_from_html_file.find(IMG_TAG_END)
            if line_position_end > -1:
                current_line_left = item.split(IMG_TAG_END)
                for line_src in current_line_left:
                    src_tag_closing_position = line_src.find(
                        IMG_SRC_TAG_END)
                    if src_tag_closing_position > -1:
                        path_to_svg = item.split(
                            IMG_SRC_TAG_END)

                        svg_image_path = extract_svg_file_path(
                            path_to_svg)

                        if svg_image_path.endswith(SVG_EXTENSION):
                            with open(svg_image_path) as html_with_svg_file:
                                svg_image = html_with_svg_file.readlines()

                                line_from_html_file = new_line_with_embedded_svg(
                                    drop_the_first_line, svg_image, line_from_html_file)

    temp_file.write(line_from_html_file)


def drop_the_first_line(svg_image):
    if len(svg_image) > 1:
        svg_image = svg_image[1:]
    return (svg_image[0])


def new_line_with_embedded_svg(drop_the_first_line, svg_image, line_from_html_file):
    line_from_html_file = "<p>" + \
        drop_the_first_line(
            svg_image) + "</p>\n"
    return line_from_html_file


def extract_svg_file_path(path_to_svg):
    path_to_svg = path_to_svg[1].split('" alt=')
    svg_image_path = path_to_svg[0].replace(
        "./../.", "").replace("./.", "")
    svg_image_path = "." + svg_image_path.strip()
    return svg_image_path


main()

from bs4 import BeautifulSoup
import unicodedata

BASE_URL = 'https://stinet.southeasttech.edu'

REMOVE_ATTRIBUTES = [
    'lang', 'language', 'onmouseover', 'onmouseout', 'script', 'style', 'font',
    'dir', 'face', 'size', 'color', 'style', 'class', 'width', 'height', 'hspace',
    'border', 'valign', 'align', 'background', 'bgcolor', 'text', 'link', 'vlink',
    'alink', 'cellpadding', 'cellspacing']


def getClassInfo(class_URL_base, browser):
    info_url = f"{class_URL_base}Main_Page.jnz"
    browser.open(info_url)
    class_info = browser.get_current_page()

    # gathers the HTML of the class info section
    class_info_section = class_info.find(class_='pi_About_This_Course') \
        .find(class_='pSection') \
        .find(class_='wysiwygtext') \
        .contents

    # Turns the HTML object and turns it into a string to remove all gaps between tags
    class_info_without_gaps = str(class_info_section).replace('> <', '><')

    # Turn the string of HTML tags back into an HTML object
    class_info_section = BeautifulSoup(
        class_info_without_gaps, features="lxml")

    sections = [
        section for section in class_info_section.find_all(name='span')]

    sections = [section.get_text().strip() for section in sections]

    sections = [unicodedata.normalize('NFKD', section)
                for section in sections]

    # return sections
    return ' '.join(sections)


def getCurrentGrade(class_url_base, browser):
    gradebook_url = f"{class_url_base}Gradebook.jnz"

    browser.open(gradebook_url)

    current_grade = browser.get_current_page().find(class_='finalGradeValue').text

    return current_grade


def getAssignmentInstructions(url, browser):
    # Go to the assignment's specific page
    browser.open(url)
    assignment_page = browser.get_current_page()

    # Go to the instructions section and gather additional instructions if they exist
    instructions = assignment_page.find(
        'div', class_='studentAssignmentInfo').find_all('div', class_='wysiwygtext')

    # Create a beautifulSoup object to store entire children elements
    instruction_content = BeautifulSoup()

    edited_instructions = []

    # Loop through elements that contain instruction content
    for section in instructions:
        # Within all elements that contain instruction content, loop through all direct children
        for child in section.find_all(True, recursive=False):
            # remove unicode encoding, and strip text of element to check if element is empty
            if ''.join([i if ord(i) < 128 else ' ' for i in child.text]).strip():
                # first strip non-empty elements of all attributes and add it to our beautifulSoup object
                for attribute in REMOVE_ATTRIBUTES:
                    del child[attribute]
                instruction_content.append(child)

    instructions = instruction_content.select('div, p')

    instructions = [instruction.text for instruction in instructions]

    for instruction in instructions:
        edited_instructions.append(
            ''.join([i if ord(i) < 128 else ' ' for i in instruction]).strip())

    # convert all instruction content to a string, and strip of unicode characters, add to our assignment object
    return edited_instructions


def getAssignmentFiles(url, browser):
    browser.open(url)
    assignment_page = browser.get_current_page()

    files_sect = assignment_page.find('div', class_='fileDisplay')
    files = []
    if files_sect:
        # Look in all of the a tags for the file information
        for file in files_sect.find_all('a'):
            # Grab the file information and add it to our files array
            files.append({
                'name': file.text,
                'url': f"{BASE_URL}{file['href']}"
            })
    return files

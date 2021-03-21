#!/usr/bin/env python

from bs4 import BeautifulSoup
import mechanicalsoup
import os
from base64 import b64decode
from nacl.secret import SecretBox
import json

REMOVE_ATTRIBUTES = [
    'lang', 'language', 'onmouseover', 'onmouseout', 'script', 'style', 'font',
    'dir', 'face', 'size', 'color', 'style', 'class', 'width', 'height', 'hspace',
    'border', 'valign', 'align', 'background', 'bgcolor', 'text', 'link', 'vlink',
    'alink', 'cellpadding', 'cellspacing']

BASE_URL = 'https://stinet.southeasttech.edu'

SECRET_KEY = os.environ.get('SECRET_KEY')

def main(username, password):
    encrypted_password = password.split(':')

    # We decode the two bits independently
    nonce = b64decode(encrypted_password[0])
    encrypted = b64decode(encrypted_password[1])

    # We create a SecretBox, making sure that out secret_key is in bytes
    box = SecretBox(bytes(SECRET_KEY, encoding='utf8'))
    decrypted_password = box.decrypt(encrypted, nonce).decode('utf-8')

    class_data = []

    # Create a browser object
    browser = mechanicalsoup.StatefulBrowser()

    # "Opens the browser up so we can start scraping"
    browser.open(BASE_URL)

    # Selects the form that we want to submit
    browser.select_form('form[action="/ics"]')

    # Selects the fields to imput data in based on the name attribute of the input element
    browser["userName"] = username
    browser["password"] = decrypted_password

    # Finds the submit button within your form and "hits" it.
    response = browser.submit_selected()

    # Creates an HTML "map" that can be parsed
    content = browser.get_current_page()

    # Grabs the section of the HTML listing the users courses
    courses = content.find('ul', attrs={'id': 'myCourses'})
    if not courses:
        return {
            'error': 'Invalid Username or Password',
            'header_info': response.headers
        }

    # Loops through each class in list and gets the name, and the url and adds it to an object
    for course in courses.find_all('a'):
        class_name = course.text.replace('  ', ' ')
        class_url = f"{BASE_URL}{course['href']}Coursework.jnz"

        # Open the coursework page for current class
        browser.open(class_url)
        coursework = browser.get_current_page()

        # Grab the assignments within the "due next" section
        assignments = coursework.find(
            'div', attrs={'id': 'pg0_V__dueNext_DueNextDiv'})

        # Loop through all assignments in the current class
        all_assignments = []
        for assignment in assignments.find_all('div', class_='dueNextAssignment'):
            # Gather information on the coursework page
            assignment = {
                'name': assignment.find('a').text,
                'due_date': assignment.find('strong').text,
                'link': f"{BASE_URL}{assignment.find('a')['href']}"
            }

            # Go to the assignment's specific page
            browser.open(assignment['link'])
            assignment_page = browser.get_current_page()

            # Go to the instructions section and gather additional instructions if they exist
            instructions = assignment_page.find(
                'div', class_='studentAssignmentInfo').find_all('div', class_='wysiwygtext')

            # Create a beautifulSoup object to store entire children elements
            instruction_content = BeautifulSoup()

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
                # convert all instruction content to a string, and strip of unicode characters, add to our assignment object
                assignment.update({
                    'instructions': ''.join([i if ord(i) < 128 else ' ' for i in str(instruction_content)])
                })

            # Gather file information if it exists
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
                # Add our array of file objects and add it to our assignment object
                assignment.update({'files': files})

            # Add our current assignment's assignment object to our array of all assignments for the current class
            all_assignments.append(assignment)

        # Add the current class's information and assignments to our class_data object
        class_data.append({
            'name': class_name,
            'link': class_url,
            'assignments': all_assignments
        })

    # Display the current JSON object
    return json.dumps(class_data)


if __name__ == '__main__':
    main()

import mechanicalsoup
from base64 import b64decode
from nacl.secret import SecretBox
from . import scrapeutils as scraper
import os

BASE_URL = 'https://stinet.southeasttech.edu'

SECRET_KEY = os.environ.get('SECRET_KEY', None)
# SECRET_KEY = 'b10dcd22075319347f196d65e1e61f6a'


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
        class_url_base = f"{BASE_URL}{course['href']}"
        class_name = course.text.replace('  ', ' ')
        class_grade = scraper.getCurrentGrade(class_url_base, browser)
        class_summary = scraper.getClassInfo(class_url_base, browser)
        # Open the coursework page for current class
        class_url = f"{class_url_base}Coursework.jnz"
        browser.open(class_url)
        coursework = browser.get_current_page()

        # Grab the assignments within the "due next" section
        assignments = coursework.find(
            'div', attrs={'id': 'pg0_V__dueNext_DueNextDiv'})

        # Loop through all assignments in the current class
        all_assignments = []
        for assignment in assignments.find_all('div', class_='dueNextAssignment'):
            # Gather information on the coursework page
            assignment_data = {
                'name': assignment.find('a').text,
                'due_date': assignment.find('strong').text,
                'link': f"{BASE_URL}{assignment.find('a')['href']}"
            }
            assignment_data.update({
                'instructions': scraper.getAssignmentInstructions(f"{BASE_URL}{assignment.find('a')['href']}", browser),
                'files': scraper.getAssignmentFiles(f"{BASE_URL}{assignment.find('a')['href']}", browser)
            })

            all_assignments.append(assignment_data)

        # Add the current class's information and assignments to our class_data object
        class_data.append({
            'name': class_name,
            'grade': class_grade,
            'summary': class_summary,
            'link': class_url,
            'assignments': all_assignments
        })

    # Display the current JSON object
    return class_data


if __name__ == '__main__':
    main()

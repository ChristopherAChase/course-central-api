# course-central-api

# Purpose
This project was a supplement to my react application called AssignmentHub. This is a simple python flask API that hosts one endpoint. This endpoint invokes a python script that goes to the Southeast Technical College website (where I was going to school at the time of creation), and scrapes the site and gathers data about the next two assignments in each of a students courses. 

# Results
When calling the API, we pass it a username, and an encrypted password from my react application. From there, it decrypts the password, and then goes on its merry way scraping the site. When it is done scraping the site, going through each of a student's current courses it returns a JSON object with the following data:
- Class Name
- Class Code
- Student's current grade in the class, both letter and percentage like so: A (96.6%)
- The general class overview from the courses main page
- The next two assignments with data including
  - The assignment name
  - The Assignment due date
  - Instructions provided by the teacher
  - Files for the assignment, if any.

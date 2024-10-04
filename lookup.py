import sqlite3
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys


# Database connection and initialization functions
def connect_to_db():
    """
    Establish a connection to the SQLite database and return a connection and cursor.
    """
    try:
        conn = sqlite3.connect("HyperionDev.db")
        cur = conn.cursor()
        return conn, cur
    except sqlite3.Error as e:
        print(f"\nError occurred while connecting to the database: {e}")
        sys.exit(1)


def initialize_db(cur):
    """
    Initialize the database by executing the SQL script.

    This function reads and executes SQL commands from the 'create_database.sql'
    file to set up the database schema. If the SQL file is not found, the program
    exits with an error message.

    Parameters:
    cur (sqlite3.Cursor): The cursor object used to execute the SQL script.

    Raises:
    FileNotFoundError: If the 'create_database.sql' file is not found.
    """
    try:
        with open('create_database.sql', 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()
        cur.executescript(sql_script)
    except FileNotFoundError:
        print("\nError: SQL script file 'create_database.sql' not found.")
        sys.exit(1)


# Data storage functions for JSON and XML formats
def store_data_as_json(data, filename):
    """
    Convert the given data to JSON format and save it to the specified file.

    Parameters:
    data (dict or list): The data to be converted to JSON.
    filename (str): The name of the file where the JSON data will be saved.

    Raises:
    Exception: If the data cannot be written to the file, an appropriate exception will be raised.
    """
    json_data = json.dumps(data, indent=4)  # Format the JSON data with indentation
    with open(filename, 'w', encoding='utf-8') as json_file:  # Open the file with UTF-8 encoding
        json_file.write(json_data)
    print(f"\nData successfully written to {filename}")


def store_data_as_xml(data, filename):
    """
    Convert the given data to XML format, pretty-print it, and save it to the specified file.

    Parameters:
    data (dict or list): The data to be converted to XML.
    filename (str): The name of the file where the XML data will be saved.

    Raises:
    ValueError: If the data is not a dictionary or a list of dictionaries, an error will be raised.
    """
    root = ET.Element("data")

    # Check if the data is a list of dictionaries or a single dictionary
    if isinstance(data, list):
        for item in data:
            item_element = ET.SubElement(root, "item")
            for key, value in item.items():
                child = ET.SubElement(item_element, key)
                child.text = str(value)
    elif isinstance(data, dict):
        for key, value in data.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
    else:
        raise ValueError("Data must be a dictionary or a list of dictionaries to store as XML.")

    # Convert to pretty-printed XML format
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Write the XML data to the file
    with open(filename, 'w', encoding='utf-8') as xml_file:
        xml_file.write(pretty_xml)
    print(f"\nData successfully written to {filename}")


# Offer to store data as a file (either XML or JSON)
def offer_to_store(data):
    """
    Prompt the user to save the given data as either an XML or JSON file.

    Parameters:
    data (dict or list): The data to be stored.

    Raises:
    ValueError: If the user enters an invalid file extension or an invalid input.
    """
    while True:
        print("\nWould you like to save this result as a file?")
        try:
            choice = int(input("\nEnter 1 for Yes or 2 for No: "))
            if choice == 1:
                while True:
                    filename = input("\nSpecify filename. Must end in .xml or .json: ").strip()

                    # Check for valid filename and extension
                    if not filename or '.' not in filename or filename.split(".")[0] == "":
                        print("\nInvalid filename. Please enter a valid filename with a base name and .xml or .json extension.")
                        continue

                    ext = filename.split(".")[-1].lower()
                    if ext == 'xml':
                        store_data_as_xml(data, filename)
                        return
                    elif ext == 'json':
                        store_data_as_json(data, filename)
                        return
                    else:
                        print("\nInvalid file extension. Please use .xml or .json.")
            elif choice == 2:
                print("\nNo file will be saved.")
                return
            else:
                print("\nInvalid choice. Please enter 1 for Yes or 2 for No.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number (1 for Yes, 2 for No).")


# Function to allow returning to the main menu
def go_back_to_menu():
    """
    Prompt the user to return to the main menu.

    Returns:
    bool: True if the user chooses to go back to the menu, otherwise False.
    """
    while True:
        choice = input("\nEnter 'B' to go back to the main menu or any other key to continue: ").upper().strip()
        if choice == 'B':
            return True
        else:
            return False


# Fetch student and course information from the database
def get_student_info(cur, student_id):
    """
    Fetch and return student information (first name, last name, and email) by student_id.

    Parameters:
    cur (sqlite3.Cursor): Cursor object to execute SQL queries.
    student_id (str): The ID of the student to fetch information for.

    Returns:
    tuple: A tuple containing the first name, last name, and email of the student.
    """
    cur.execute('''SELECT first_name, last_name, email FROM Student WHERE student_id=?''', (student_id,))
    return cur.fetchone()


def get_course_name(cur, course_code):
    """
    Fetch and return the course name by course_code.

    Parameters:
    cur (sqlite3.Cursor): Cursor object to execute SQL queries.
    course_code (str): The course code to fetch the course name for.

    Returns:
    str: The name of the course.
    """
    cur.execute('''SELECT course_name FROM Course WHERE course_code=?''', (course_code,))
    return cur.fetchone()[0]


# List all student names
def all_student_names(cur):
    """
    Display all student names and surnames from the database.

    Parameters:
    cur (sqlite3.Cursor): Cursor object to execute SQL queries.

    This function retrieves all students' first names and last names from the database,
    displays them in a numbered list, and then offers to store the data as XML or JSON.
    """
    cur.execute("SELECT first_name, last_name FROM Student")
    data = cur.fetchall()

    if data:
        print("\n\033[1mStudent names and surnames:\033[0m\n")
        students_data = [{"first_name": firstname, "last_name": surname} for firstname, surname in data]

        # Display students in a numbered list
        for i, student in enumerate(students_data, 1):
            print(f"{i}. {student['first_name']} {student['last_name']}")

        # Offer to store the retrieved student data
        offer_to_store(students_data)
    else:
        print("\nNo students found.")


# View subjects taken by a student
def view_subjects_by_student(cur):
    """
    Display the subjects taken by a student based on the provided student_id.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.

    The function allows the user to input a student_id, fetches the course codes
    associated with the student from the 'StudentCourse' table, and displays the
    course names from the 'Course' table. If the student ID is incorrect, the user
    is prompted to re-enter the ID or go back to the main menu.
    """
    while True:

        student_id = input("\nEnter student ID: ").upper().strip()
        cur.execute('''SELECT course_code FROM StudentCourse WHERE student_id=?''', (student_id,))
        courses = cur.fetchall()

        if courses:
            # Fetch course names using the retrieved course codes
            course_codes = [course[0] for course in courses]
            placeholders = ', '.join(['?'] * len(course_codes))
            cur.execute(f"SELECT course_name FROM Course WHERE course_code IN ({placeholders})", course_codes)
            subjects = cur.fetchall()

            if subjects:
                # Display the subjects taken by the student
                subjects_data = [{"course_name": subject[0]} for subject in subjects]
                print("\n\033[1mSubjects taken by the student:\033[0m")
                for subject_data in subjects_data:
                    print(f"\n\033[1mCourse Name:\033[0m {subject_data['course_name']}")
                offer_to_store(subjects_data)  # Offer to store the data
            else:
                print("\nNo subjects found for this student.")
            break
        else:
            print(f"\nIncorrect student ID {student_id}. Please try again.")
            if go_back_to_menu():
                return  # Return to the main menu if 'B' is pressed


# Lookup address by student's name
def lookup_address_by_name(cur):
    """
    Lookup the address of a student using their first name and surname.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.

    The function allows the user to input a student's first name and surname,
    fetches the address ID associated with the student from the 'Student' table,
    and displays the street and city from the 'Address' table. If no student or
    address is found, the user is prompted to try again or go back to the main menu.
    """
    while True:

        firstname = input("Enter first name: ").capitalize().strip()
        surname = input("Enter surname: ").capitalize().strip()
        cur.execute('''SELECT address_id FROM Student WHERE first_name=? AND last_name=?''', (firstname, surname))
        address_id = cur.fetchone()

        if address_id:
            # Fetch the address details using the address ID
            cur.execute('''SELECT street, city FROM Address WHERE address_id=?''', (address_id[0],))
            address = cur.fetchone()

            if address:
                # Display the fetched address
                address_data = {"street": address[0], "city": address[1]}
                print("\n\033[1mAddress\033[0m")
                for key, value in address_data.items():
                    print(f"\n\033[1m{key.capitalize()}:\033[0m {value}")
                offer_to_store(address_data)  # Offer to store the address data
            else:
                print("\nNo address found for this student.")
            break
        else:
            print(f"\nNo student found with the name {firstname} {surname}. Please try again.")
            if go_back_to_menu():
                return  # Return to the main menu if 'B' is pressed


# List reviews for a student
def list_reviews_by_student(cur):
    """
    List all reviews for a given student based on their student_id.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.

    The function allows the user to input a student_id, fetches reviews associated
    with the student from the 'Review' table, and displays details of the review,
    including course code, completeness, efficiency, style, documentation, and review text.
    If no reviews are found, the user is prompted to try again or return to the main menu.
    """
    while True:

        student_id = input("Enter student ID: ").upper().strip()
        cur.execute(
            '''SELECT course_code, completeness, efficiency, style, documentation, review_text
               FROM Review WHERE student_id=?''', (student_id,)
        )
        reviews = cur.fetchall()

        if reviews:
            # Prepare review data as a list of dictionaries
            reviews_data = [
                {
                    "course_code": review[0],
                    "completeness": review[1],
                    "efficiency": review[2],
                    "style": review[3],
                    "documentation": review[4],
                    "review_text": review[5]
                }
                for review in reviews
            ]

            # Display reviews for the student
            print(f"\n\033[1mReviews for student with ID {student_id}:\033[0m\n(NB: Ratings are out of 4)\n")
            for review_data in reviews_data:
                print(f"\033[1mCourse Code:\033[0m {review_data['course_code']}")
                print(f"\033[1mCompleteness:\033[0m {review_data['completeness']}")
                print(f"\033[1mEfficiency:\033[0m {review_data['efficiency']}")
                print(f"\033[1mStyle:\033[0m {review_data['style']}")
                print(f"\033[1mDocumentation:\033[0m {review_data['documentation']}")
                print(f"\033[1mReview Text:\033[0m {review_data['review_text']}\n")

            offer_to_store(reviews_data)  # Offer to store the review data
            break
        else:
            print(f"\nNo reviews found for student with ID {student_id}. Please try again.")
            if go_back_to_menu():
                return  # Return to the main menu if 'B' is pressed


# List all courses offered by a teacher
def list_courses_by_teacher(cur):
    """
    List all courses offered by a teacher based on the teacher_id input.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.

    The function allows the user to input a teacher_id, fetches courses associated
    with the teacher from the 'Course' table, and displays the course names.
    If no courses are found, the user is prompted to try again or return to the main menu.
    """
    while True:

        teacher_id = input("Enter teacher ID: ").upper().strip()
        cur.execute('''SELECT course_name FROM Course WHERE teacher_id=?''', (teacher_id,))
        courses = cur.fetchall()

        if courses:
            # Prepare course data as a list of dictionaries
            subjects_data = [{"teacher_id": teacher_id, "course_name": course[0]} for course in courses]

            # Display courses offered by the teacher
            print(f"\n\033[1mCourses offered by teacher with ID {teacher_id}:\033[0m")
            for course in subjects_data:
                print(f"\n\033[1mCourse Name:\033[0m {course['course_name']}")

            offer_to_store(subjects_data)  # Offer to store the course data
            break
        else:
            print(f"\nNo courses found for teacher with ID {teacher_id}. Please try again.")
            if go_back_to_menu():
                return  # Return to the main menu if 'B' is pressed


# List students who haven't completed their course
def list_students_not_completed(cur):
    """
    List all students who haven't completed their courses.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.

    This function retrieves and displays a list of students who have not completed their courses.
    It also offers the option to store the data in a file.
    """
    cur.execute('''SELECT student_id, course_code FROM StudentCourse WHERE is_complete = 0''')
    incomplete_courses = cur.fetchall()

    if incomplete_courses:
        incomplete_data = []
        print("\n\033[1mStudents who have not completed their courses:\033[0m\n")

        # Fetch student info and course name for each incomplete course
        for count, (student_id, course_code) in enumerate(incomplete_courses, 1):
            student_info = get_student_info(cur, student_id)
            course_name = get_course_name(cur, course_code)

            if student_info:
                first_name, last_name, email = student_info
                # Display student details along with the course name
                print(f"{count}. {student_id} {first_name} {last_name} ({email}) - Course: {course_name}")
                incomplete_data.append({
                    "student_id": student_id,
                    "course_code": course_code,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "course_name": course_name
                })
        offer_to_store(incomplete_data)  # Offer to store the incomplete course data
    else:
        print("\nNo students have incomplete courses.")


# List students with low marks
def list_students_with_low_marks(cur):
    """
    List all students who have completed their courses and achieved a mark of 30 or below.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.

    This function retrieves and displays a list of students who have completed their courses
    but scored 30 or below. It also offers the option to store the data in a file.
    """
    cur.execute('''SELECT student_id, course_code, mark FROM StudentCourse WHERE mark <= 30''')
    low_courses = cur.fetchall()

    if low_courses:
        low_data = []
        print("\n\033[1mStudents who have a mark below 30:\033[0m\n")

        # Fetch student info, course name, and mark for each low score
        for count, (student_id, course_code, mark) in enumerate(low_courses, 1):
            student_info = get_student_info(cur, student_id)
            course_name = get_course_name(cur, course_code)

            if student_info:
                first_name, last_name, email = student_info
                # Display student details, course name, and the mark
                print(f"{count}. {student_id} {first_name} {last_name} ({email}) - Course: {course_name} - Mark: {mark}")
                low_data.append({
                    "student_id": student_id,
                    "course_code": course_code,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "course_name": course_name,
                    "mark": mark
                })
        offer_to_store(low_data)  # Offer to store the low score data
    else:
        print("\nNo students have a mark below 30.")


# Exit the program and close the database connection
def exit_program(conn):
    """
    Close the database connection and exit the program.

    Parameters:
    conn (sqlite3.Connection): The database connection to be closed.
    """
    conn.close()  # Close the database connection
    print("\nProgram exited successfully!")
    sys.exit(0)  # Exit the program


# Main menu options
def menu_options(cur, conn):
    """
    Display the main menu and handle user input for selecting options.

    Parameters:
    cur (sqlite3.Cursor): Cursor object used to execute SQL queries.
    conn (sqlite3.Connection): Connection object used to manage the database connection.

    This function continuously prompts the user to select an option from the menu and
    performs the corresponding action (view students, subjects, reviews, etc.). The user
    can also exit the program, which closes the database connection.
    """
    menu_text = '''
    What would you like to do?

    1 - View all students
    2 - View subjects taken by a student
    3 - Lookup address for a student
    4 - List reviews for a student
    5 - List all courses given by a teacher
    6 - List all students who have not completed their course
    7 - List all students who have completed their course and achieved 30 or below
    8 - Exit this program

    Type your option here: '''

    print("\033[1mWelcome to the HyperionDev Query APP!\033[0m")

    while True:
        try:
            user_input = int(input(menu_text))  # Get user input and convert it to an integer
            print()

            # Match user input to corresponding function calls
            if user_input == 1:
                all_student_names(cur)
            elif user_input == 2:
                view_subjects_by_student(cur)
            elif user_input == 3:
                lookup_address_by_name(cur)
            elif user_input == 4:
                list_reviews_by_student(cur)
            elif user_input == 5:
                list_courses_by_teacher(cur)
            elif user_input == 6:
                list_students_not_completed(cur)
            elif user_input == 7:
                list_students_with_low_marks(cur)
            elif user_input == 8:
                exit_program(conn)  # Exit the program and close the connection
            else:
                print("\nInvalid option. Please select a number between 1 and 8.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")


# Main function
def main():
    """
    Initialize the database and display the main menu.

    This function establishes a connection to the database, initializes the database
    schema (if needed), and displays the menu for the user to interact with.
    """
    conn, cur = connect_to_db()  # Establish database connection and get cursor
    initialize_db(cur)  # Initialize the database schema
    menu_options(cur, conn)  # Display the menu options


if __name__ == "__main__":
    main()


"""References:
https://stackoverflow.com/questions/583562/json-character-encoding-is-utf-8-well-supported-by-browsers-or-should-i-use-nu
https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used
https://www.datacamp.com/tutorial/how-to-exit-python-a-quick-tutorial
https://stackoverflow.com/questions/14639077/how-to-use-sys-exit-in-python
https://docs.python.org/3/library/xml.dom.minidom.html
https://stackoverflow.com/questions/3605680/creating-a-simple-xml-file-using-python
https://stackoverflow.com/questions/68761820/how-to-print-bold-font-when-using-f-string
https://stackoverflow.com/questions/44689546/how-to-print-out-a-dictionary-nicely-in-python
https://pieriantraining.com/counting-in-a-python-loop-a-beginners-guide/#:~:text=The%20%60for%60%20loop%20then%20iterates,()%60%20and%20prints%20it%20out.&text=In%20this%20example%2C%20we%20initialize,print%20out%20the%20total%20count.
https://www.w3schools.com/python/ref_func_isinstance.asp
https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
https://stackoverflow.com/questions/59613778/save-data-in-xml-file-in-python
https://www.bacancytechnology.com/qanda/python/return-sql-data-in-json-format-python
https://stackoverflow.com/questions/25371636/how-to-get-sqlite-result-error-codes-in-python
https://stackoverflow.com/questions/54289555/how-do-i-execute-an-sqlite-script-from-within-python
https://stackoverflow.com/questions/19472922/reading-external-sql-script-in-python
"""

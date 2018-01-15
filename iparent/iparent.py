#!/usr/bin/env python3

"""Download report from iparent portal"""

import requests
import http.cookiejar
import json
import re
import os
import getpass

headers = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/63.0.3239.132 Safari/537.36'
}


def login(username, password):
    """login iparent portal"""
    url = 'https://parentslogin.kidsoft.com.au/index.php/Login/login'
    data = {
        'Username': username,
        'Password': password,
        'controller': 'Login',
        'action': 'login'
    }
    result = session.post(url, data=data, headers=headers)
    if json.loads(result.text)['Status'] == 'OK':
        session.cookies.save(ignore_discard=True, ignore_expires=True)
        print('Login successfully!')
        redirect = json.loads(result.text)['Payload']['RedirectURL']
        session.get(redirect, headers=headers)
        session.cookies.save(ignore_discard=True, ignore_expires=True)
        return True
    else:
        print(json.loads(result.text))
        return False


def download_doc():
    """download the reports"""
    url = 'https://parents.kidsoft.com.au/index.php/ParentPortal/ParentPortalDownload/prepareDownloadList'
    data = {
        'controller': 'ParentPortal/ParentPortalDownload',
        'action': 'prepareDownloadList'
    }
    response = session.post(url, data=data, headers=headers)
    doc_list = json.loads(response.text)['Payload']['Records']
    for doc in doc_list:
        date = doc['Date']
        description = doc['Description']
        if re.match(r'^201[7|8].*', date):
            doc_name = (date + '-' + description).replace("/", "-")
            doc_url = 'https://parents.kidsoft.com.au'+doc['DownloadURL']
            download(doc_name, doc_url)


def download(name, url):
    """download url"""
    if not os.path.isfile('./downloads/'+name):
        print('downloading ' + name)
        doc = session.get(url, headers=headers)
        with open('./downloads/'+name, 'wb') as f:
            f.write(doc.content)
    else:
        print(name + ' is already there.')


if __name__ == '__main__':
    Username = input('Username: ')
    Password = getpass.getpass('Password: ')
    session = requests.session()
    session.cookies = http.cookiejar.LWPCookieJar('cookie')
    login(Username, Password)
    try:
        session.cookies.load(ignore_discard=True)
        download_doc()
    except IOError:
        print('Cookies is not found')


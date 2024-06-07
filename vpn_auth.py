import requests
import re
import os
import json
import time
import getpass
import subprocess
from bs4 import BeautifulSoup

vpn_url = os.environ['VPN_URL']
vpn_group = os.environ['VPN_GROUP']
username = os.environ['VPN_USER']

print(f"Connecting to {vpn_url} as {username}")
password = getpass.getpass("Enter VPN Password: ")

s = requests.Session()

landing_page = s.get(vpn_url + "/+CSCOE+/logon.html")

soup = BeautifulSoup(landing_page.text, 'html.parser')
csrf_token_element = soup.find('input', {'name': 'csrf_token'})
csrf_token = csrf_token_element['value']

body = {
    "tgroup": "",
    "next": "",
    "tgcookieset": "",
    "csrf_token": csrf_token,
    "group_list": vpn_group,
    "Login": "Logon"
}

saml_auth_response = s.post(vpn_url +"/+CSCOE+/saml/sp/login", data=body)

m = re.search(r'\$Config=\{(.+)\};', saml_auth_response.text)
page = json.loads('{' + m.group(1) + '}')


login_data = {
    'i13': '1',
    'login': username,
    'loginfmt': username,
    'type': '11',
    'LoginOptions': '3',
    'lrt': '',
    'lrtPartition': '',
    'hisRegion': '',
    'hisScaleUnit': '',
    'passwd': password,
    'ps': '2',
    'psRNGCDefaultType': '',
    'psRNGCEntropy': '',
    'psRNGCSLK': '',
    'canary': page['canary'],
    'ctx': page.get('sCtx', page.get('Ctx')),
    'hpgrequestid': page['sessionId'],
    'flowToken': page['sFT'] or page['oGetCredTypeResult']['FlowToken'],
    'PPSX': '',
    'NewUser': '1',
    'FoundMSAs': '',
    'fspost': '1',
    'i21': '0',
    'CookieDisclosure': '0',
    'IsFidoSupported': '0',
    'isSignupPost': '0',
    'i19': '56628'
}

urlPost = page['urlPost']
urlPost = 'https://login.microsoftonline.com' + urlPost
login_response = s.post(urlPost, data=login_data)

m = re.search(r'\$Config=\{(.+)\};', login_response.text)
page = json.loads('{' + m.group(1) + '}')

if 'arrUserProofs' in page and len( page['arrUserProofs'] ) > 0:
    pollcount = 1
    canary = page['canary']
    data = {"AuthMethodId":"PhoneAppNotification","Method":"BeginAuth","ctx":page['sCtx'],"flowToken":page['sFT']}
    mfa_response = s.post("https://login.microsoftonline.com/common/SAS/BeginAuth",json=data, headers={'Canary':page['apiCanary']}).json()
    
    if mfa_response.get('Entropy') != None:
        print(f"Approve the MFA prompt with code: {mfa_response.get('Entropy')}!")
    else:
        print(f"Approve the MFA prompt!")
    

    pollCount = 1
    lastPollStart = None
    lastPollEnd = int( time.time() ) * 1000
    
    while True: 
        lastpollstart = int( time.time() ) * 1000
        url = 'https://login.microsoftonline.com/common/SAS/EndAuth?authMethodId='+data['AuthMethodId']+'&pollCount='+str(pollcount) 
        if pollcount > 1:
            url += '&lastPollStart='+str(lastpollstart)+'&lastPollEnd='+str(lastPollEnd)
        pollcount += 1
        rtn = s.get( url, headers={
      'X-Ms-Flowtoken': mfa_response.get('FlowToken'),
      'X-Ms-Ctx': mfa_response.get('Ctx'),
      'X-Ms-Sessionid': mfa_response.get('SessionId'),
      'Canary': canary
        } ).json()
        lastpollend = int( time.time() ) * 1000
        time.sleep(1)
        if rtn['Success']: break
    print(rtn['ResultValue'])
        
    lastpollstart = int( time.time() ) * 1000
    headers = {
        "Origin": "https://login.microsoftonline.com",
        "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, */*;q=0.8",
        "Referer": "https://login.microsoftonline.com/common/login",
        "Connection": "close",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Te": "trailers",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Language": "en-GB, en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    login_response = s.post(
      'https://login.microsoftonline.com/common/SAS/ProcessAuth',
      data = {
        'type': '22',
        'request': rtn['Ctx'],
        'mfaLastPollStart': lastpollstart,
        'mfaLastPollEnd': lastpollend,
        'mfaAuthMethod': rtn['AuthMethodId'],
        'rememberMFA': 'true',
        'login': username,
        'flowToken': rtn['FlowToken'],
        'hpgrequestid': rtn['SessionId'],
        'sacxt': '',
        'hideSmsInMfaProofs': 'false',
        'canary': canary,
        'i19': '11302'
      },
      headers=headers
    )

    m = re.search(r'\$Config=\{(.+)\};', login_response.text)
    kmsi_page = json.loads('{' + m.group(1) + '}')
    kmsi_data = {
      'LoginOptions': '1',
      'type': '28',
      'ctx': kmsi_page['sCtx'],
      'hpgrequestid': kmsi_page['sessionId'],
      'flowToken': kmsi_page['sFT'],
      'canary': kmsi_page['canary'], 
      'i19': '3233',
      'DontShowAgain': 'true'
    }
    kmsi_response = s.post( 'https://login.microsoftonline.com/kmsi', data=kmsi_data )     

    soup = BeautifulSoup(kmsi_response.content, 'html.parser')
    saml_response = soup.find('input', {'name': 'SAMLResponse'})['value']
    form = soup.find('form', {'name': 'hiddenform'})
    submit_url = form['action']
    data = {
        "SAMLResponse": saml_response
    }
    submit_response = s.post(submit_url, data=data)
    
    final_soup = BeautifulSoup(submit_response.text, 'html.parser')

    # Extract the csrf_token
    csrf_token = final_soup.find('input', {'name': 'csrf_token'})['value']

    # Extract the final form action URL
    final_form = final_soup.find('form', {'id': 'samlform'})
    final_submit_url = final_form['action']

    # Extract other necessary form values
    tgroup = final_form.find('input', {'name': 'tgroup'})['value']
    next_val = final_form.find('input', {'name': 'next'})['value']
    tgcookieset = final_form.find('input', {'name': 'tgcookieset'})['value']
    group_list = final_form.find('input', {'name': 'group_list'})['value']
    username = final_form.find('input', {'name': 'username'})['value']
    password = final_form.find('input', {'name': 'password'})['value']

    # The final data to be submitted with the form
    final_data = {
        "tgroup": tgroup,
        "next": next_val,
        "tgcookieset": tgcookieset,
        "csrf_token": csrf_token,
        "group_list": group_list,
        "username": username,
        "password": password,
        "SAMLResponse": saml_response
    }

    cookies = {
        "CSRFtoken": csrf_token,
        "webvpnlogin": "1",
        "webvpnLang": "en"
    }

    final_submit_response = requests.post(vpn_url + final_submit_url, data=final_data,cookies=cookies)
    
    vpn_cookie = final_submit_response.cookies['webvpn']
    
    subprocess.run(['openconnect', '--cookie', vpn_cookie, vpn_url])
    
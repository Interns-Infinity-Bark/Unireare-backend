import base64
import hmac
import time
import urllib.parse
import uuid
from hashlib import sha1

import requests


class AliyunMailSender:
    def __init__(self, access_id, access_secret):
        self.url = "https://dm.aliyuncs.com"
        self.access_id = access_id
        self.access_secret = access_secret

    def sign(self, accesskeysecret, parameters):
        sortedparameters = sorted(parameters.items(), key=lambda para: para[0])
        canonicalizedquerystring = ''
        for (k, v) in sortedparameters:
            canonicalizedquerystring += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)
        stringtosign = 'POST&%2F&' + self.percent_encode(canonicalizedquerystring[1:])
        h = hmac.new(bytes(accesskeysecret, 'utf-8') + b"&", stringtosign.encode('utf-8'), sha1)
        signature = base64.b64encode(h.digest()).strip()
        return signature

    @staticmethod
    def percent_encode(encodestr):
        return urllib.parse.quote(str(encodestr), '').replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

    def make_parameters(self, params):
        parameters = {
            'Format': 'JSON',
            'Version': '2015-11-23',
            'AccessKeyId': self.access_id,
            'SignatureVersion': '1.0',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid1()),
            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        for key in params.keys():
            parameters[key] = params[key]
        signature = self.sign(self.access_secret, parameters)
        parameters['Signature'] = signature
        return parameters

    def single_send_mail(self, account, alias, email_address, subject, text):
        payload = {
            'Action': 'SingleSendMail',
            'AccountName': account,
            'ReplyToAddress': 'false',
            'AddressType': 1,
            'ToAddress': email_address,
            'FromAlias': alias,
            'Subject': subject,
            'HtmlBody': text
        }
        request = requests.post(self.url, self.make_parameters(payload))
        return request.text

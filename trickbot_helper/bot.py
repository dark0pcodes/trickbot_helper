import hashlib
import random
import re
import struct

import requests
import urllib3
from Crypto.Cipher import AES
from requests.exceptions import ReadTimeout, HTTPError, ConnectionError

# Disable certificate warnings
urllib3.disable_warnings()


class Bot:
    def __init__(self, ver, gtag='tt0002', pc_name='SOPHIA_PC', windows_version='Windows7x86'):
        """
        Generate Bot unique ID and set configuration parameters

        :param gtag: Campaign identifier
        :param pc_name: Name of the victim's PC
        :param windows_version: Windows affected version
        :param ver: Version of the attack
        """
        self.random_str = self.generate_random_str()
        unique_id = hashlib.sha256(self.random_str.encode()).hexdigest().upper()

        self.gtag = gtag
        self.client_id = f'{pc_name}_W617600.{unique_id}'
        self.register_str = f'{windows_version}/{ver}/{self.get_my_ip()}/{unique_id}'
        self.ver = ver

    @staticmethod
    def generate_random_str():
        """
        Generate random string that will be used in the url_path

        :return:
        """
        str_len = random.randrange(0, 17) + 16
        rand_str = ''

        for i in range(0, str_len):
            char = random.randrange(0, 62)

            if char >= 52:
                char -= 4
            elif char >= 26:
                char += 71
            else:
                char += 65

            rand_str += chr(char)
        return rand_str

    @staticmethod
    def get_my_ip():
        """
        Get Public IP of the bot

        :return:
        """
        return requests.get('https://api.ipify.org', verify=False, timeout=4).text

    @staticmethod
    def parse_content(content):
        """
        Extract the useful data from the response

        :param content: Data content to be parsed
        :return:
        """
        params = content.split(b'/', 6)
        return params[6][2:int(params[5]) + 2]

    @staticmethod
    def running_sha256(content):
        """
        Trickbot proprietary hashing routine

        :param content: Data content to be hashed
        :return:
        """
        hash_data = content

        while 1:
            sha256_hash = hashlib.sha256(hash_data).digest()
            hash_data += sha256_hash

            if len(hash_data) > 0x1000:
                break
        return sha256_hash

    def decrypt(self, content):
        """
        Trickbot proprietary decryption routine

        :param content: Data content to be decrypted
        :return:
        """

        key = self.running_sha256(content[:0x20])
        iv = self.running_sha256(content[0x10:0x30])

        cipher = AES.new(key, AES.MODE_CBC, iv[:16])
        decrypted_data = cipher.decrypt(content)
        config_length = struct.unpack('<I', decrypted_data[:4])[0]
        config_length += 0x08

        return decrypted_data[0x08:config_length]

    def __query(self, server, port, url_path):
        """
        Connect to the malicious server

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :param url_path: URL path to connect
        :return:
        """
        try:
            r = requests.get(f'https://{server}:{port}/{url_path}', verify=False, timeout=60)
            r.raise_for_status()

            # Check if r is a valid response
            if self.gtag.encode() in r.content:
                return self.decrypt(self.parse_content(r.content))
            return self.decrypt(r.content)

        except (ReadTimeout, HTTPError, ConnectionError, ValueError):
            return

    def register(self, server, port):
        """
        Register to the malicious server and download the latest configuration

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :return: List of servers found in the configuration file
        """
        data = self.__query(server, port, f'{self.gtag}/{self.client_id}/0/{self.register_str}/{self.random_str}/')

        if data:
            return [server.decode() for server in re.findall(b'<psrv>(.*?)</psrv>', data)]

    def get_file(self, server, port, file_name):
        """
        Download file from the Botnet

        :return:
        """
        return self.__query(server, port, f'{self.gtag}/{self.client_id}/5/{file_name}/')

    def get_update_link(self, server, port):
        """
        Update Trickbot binary

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :return:
        """
        return self.__query(server, port, f'{self.gtag}/{self.client_id}/25/{self.random_str}/')

    def get_updated_config(self, server, port):
        """
        Update Trickbot binary

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :return:
        """
        data = self.__query(server, port, f'{self.gtag}/{self.client_id}/23/{self.ver}/')

        if data:
            ver_match = re.search(b'<ver>(.*?)</ver>', data)
            gtag_match = re.search(b'<gtag>(.*?)</gtag>', data)

            ver = data[ver_match.start() + 5:ver_match.end() - 6].decode()
            gtag = data[gtag_match.start() + 6:gtag_match.end() - 7].decode()
            return [server.decode() for server in re.findall(b'<srv>(.*?)</srv>', data)], ver, gtag

    def get_dpost(self, server, port):
        """
        Download 'dpost' configuration (used during data exfiltration)

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :return:
        """
        data = self.get_file(server, port, 'dpost')

        if data:
            return [server.decode() for server in re.findall(b'<handler>(.*?)</handler>', data)]

    def get_mailconf(self, server, port):
        """
        Download 'mailconf' configuration (used to send harvested email list to)

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :return:
        """
        data = self.get_file(server, port, 'mailconf')

        if data:
            return [server.decode() for server in re.findall(b'<handler>(.*?)</handler>', data)]

    def get_dinj(self, server, port):
        """
        Download 'dinj' configuration (web-injection targets)

        :param server: IP of the malicious server
        :param port: PORT of the malicious server
        :return:
        """
        data = self.get_file(server, port, 'dinj')

        # TODO: Try to get web injects
        # Reference: https://www.uperesia.com/how-trickbot-tricks-its-victims

        if data:
            data = re.findall(b'<lm>(.*?)</lm>|<hl>(.*?)</hl>', data)
            return [(data[i][0].decode(), data[i + 1][1].decode()) for i in range(0, len(data), 2)]

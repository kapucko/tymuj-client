from argparse import ArgumentParser
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

base = 'https://int.tymuj.cz'


class TymujCLient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.get(base)

    def login(self):
        login_params = {
            'username': self.username,
            'password': self.password,
            'Odeslat': 'Odeslat',
        }
        url = urljoin(base, 'login')
        resp = self.session.post(url, data=login_params).content
        return resp

    def _get_next_match_id(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        zapasy = soup.find_all("div", {"id": "zapasy"})
        zapas = zapasy[0]
        zapas_detail = urljoin(base, zapas.find('a')['href'])
        zapas_id = zapas_detail.rsplit('/', 1)
        return zapas_id

    def _get_next_match_page(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        zapasy = soup.find_all("div", {"id": "zapasy"})
        zapas = zapasy[0]
        zapas_detail = urljoin(base, zapas.find('a')['href'])
        resp = self.session.get(zapas_detail).content
        return resp

    def set_next_match_attendance(self, status):
        resp = self.login()
        zapas_id = self._get_next_match_id(resp)
        event_data = {
            'answer': '1' if status else '2',  # 0 - neviem 1 - ano 2 - nie
            'comment': 'Test script',
            'event': zapas_id,
            'user': '123456', # TODO dostat userid
        }
        url = urljoin(base, '/attendance/update/enhanced/0')
        resp = self.session.post(url, data=event_data)
        print(resp.status_code)

    def get_next_match_stats(self):
        resp = self.login()
        resp = self._get_next_match_page(resp)
        soup = BeautifulSoup(resp, 'html.parser')
        box = soup.find_all('div', {'class': 'box2_content'})[0]
        hraci_nevyjadreny = box.find_all('img', alt=re.compile('Attendance_button_(0_i)|(none)'))
        hraci_ano = box.find_all('img', alt=re.compile('Attendance_button_1(_i){0,1}'))
        hraci_nie = box.find_all('img', alt=re.compile('Attendance_button_2(_i){0,1}'))
        print('Neviem: {0}'.format(len(hraci_nevyjadreny)))
        print('Idem: {0}'.format(len(hraci_ano)))
        print('Nejdem: {0}'.format(len(hraci_nie)))


def main(args):
    client = TymujCLient(args.user, args.password)
    client.get_next_match_stats()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-u", "--user", action="store", help="tymuj.cz username")
    parser.add_argument("-p", "--password", action="store", help="tymuj.cz password")
    args = parser.parse_args()
    main(args)
import requests
from requests.exceptions import HTTPError
from collections import defaultdict
import logging
import os
import json

class AWSIPRanges():
    def __init__(self):
        logging.basicConfig(format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        self.logger = logging.getLogger('Builder.builder')
        self.logger.setLevel(int(os.environ.get('Logging', logging.DEBUG)))
        self.aws_ip_ranges = {}
        self.by_service = {}
        self.by_region = {}

    def get_aws_ip_ranges_payload(self, url: str = 'https://ip-ranges.amazonaws.com/ip-ranges.json') -> None:
        try:
            response = requests.get(url)
        except HTTPError as http_err:
            self.logger.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')
        else:
            self.logger.info(f'Successfully retrieved {url}')
            self.aws_ip_ranges = response.json()

    def parse_ip_ranges(self) -> None:
        for prefix in self.aws_ip_ranges.get('prefixes'):
            self.by_service.setdefault(prefix['service'], {}).setdefault(prefix['region'], []).extend(prefix['ip_prefix'])
            self.by_region.setdefault(prefix['region'], {}).setdefault(prefix['service'], []).extend(prefix['ip_prefix'])

        for prefix in self.aws_ip_ranges.get('ipv6_prefixes'):
            self.by_service.setdefault(prefix['service'], {}).setdefault(prefix['region'], []).extend(prefix['ipv6_prefix'])
            self.by_region.setdefault(prefix['region'], {}).setdefault(prefix['service'], []).extend(prefix['ipv6_prefix'])

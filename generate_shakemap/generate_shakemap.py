#!/usr/bin/env python3
import os
import sys
import re
import xml.etree.ElementTree as ET
import subprocess
import time

import logging
from logging.handlers import RotatingFileHandler

# იწერება კონფიგურაცია, რომლითაც მონაცემს წამოიღებს მიწისძვრის შესახებ
SERVER_IP = 'localhost'
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
EVENT_ID = sys.argv[2]

# გაშვებული სკრიპტის მისამართი
TEMP_DIR_PATH = SCRIPT_PATH + "/temp"
if not os.path.isdir(TEMP_DIR_PATH):
    os.mkdir(TEMP_DIR_PATH)

# log-ების მისამართი
LOGS_DIR_PATH = SCRIPT_PATH + "/logs"
if not os.path.isdir(LOGS_DIR_PATH):
    os.mkdir(LOGS_DIR_PATH)


# xml-ის და html-ის მისამართები, ასევე ბრაუზერი, რომლითან გახსნის html-ს 
XML_PATH = TEMP_DIR_PATH + "/eq_log.xml"

# logging-ის კონფიგურაცია
LOG_FILENAME = f'{LOGS_DIR_PATH}/generate_shakemap.log'
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Keep 3 backup log files

# Create a rotating file handler
rotating_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Set up the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)


# ეს ფუნქცია პასუხისმგებელია xml-ის დაგენერირებაზე სეისკომპიდან გადმოცემული event_id-ით
def xml_dump(xml_path, event_id, server_ip):
    # seiscomp exec scxmldump -APMfmp -o /home/sysop/Code/Seiscomp_Scripts/generate_shakemap/temp/eq_log.xml -E grg2025fary -d localhost
    command = f'seiscomp exec scxmldump -APMfmp -o {xml_path} -E {event_id} -d {server_ip}'
    try:
        subprocess.run(command, check=True, shell=True )
        logging.debug(f'<xml_dump - xml წარმატებით დაგენერირდა>')
    except subprocess.CalledProcessError as e:
        # print("Error:", e)
        logging.critical(f'<xml_dump - xml-ის დაგენერირების დროს დაფიქსირდა შეცდომა: {e}>')
        sys.exit(1)


if __name__ == '__main__':
    # 1) XML ფაილის დაგენერირება სეისკომპიდან scxmldump-ის გამოყენებით .
    xml_dump(XML_PATH, EVENT_ID, SERVER_IP)
    file = open(XML_PATH, "r")

    xml_file_content = re.sub(' xmlns="[^"]+"', '', file.read(), count=1)

    #String დან xml-ის "გაპარსვა"
    root = ET.fromstring(xml_file_content)
    #xml - ში origin ტეგის წაკითხვა
    eventParameters_element =  root.find('EventParameters')
    origin_element = eventParameters_element.find('origin')
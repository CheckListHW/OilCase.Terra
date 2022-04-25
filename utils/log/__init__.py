import os
from datetime import datetime
import sys
from utils.log.clear_logs import clear_logs

if not os.environ.get('input_logs'):
    os.environ['input_logs'] = os.getcwd()

if not os.path.exists(os.environ['input_logs'] + '/logs'):
    os.mkdir(os.environ['input_logs'] + '/logs')

logs_dir = os.environ['input_logs'] + '/logs'

clear_logs(logs_dir)
file_name = str(datetime.now()).replace(" ", "_").replace(":", "-")[:-7]
os.environ['logs_file_path'] = f'{logs_dir}/{file_name}.txt'

f = open(os.environ['logs_file_path'], 'x')
f.write('')
f.close()

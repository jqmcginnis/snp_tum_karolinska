import os
import shutil
from pathlib import Path
import re
from bs4 import BeautifulSoup
import numpy as np

# bids helpers
def getSubjectID(path):
    """
    :param path: path to data file
    :return: return the BIDS-compliant subject ID
    """
    stringList = str(path).split("/")
    indices = [i for i, s in enumerate(stringList) if 'sub-' in s]
    text = stringList[indices[0]]
    try:
        found = re.search(r'sub-([a-zA-Z0-9]+)', text).group(1)
    except AttributeError:
        found = ''
    return found

def getSessionID(path):
    """
    :param path: path to data file
    :return: return the BIDS-compliant session ID
    """
    stringList = str(path).split("/")
    indices = [i for i, s in enumerate(stringList) if 'ses-' in s]
    text = stringList[indices[0]]
    try:
        found = re.search(r'ses-([a-zA-Z0-9]+)', text).group(1)
    except AttributeError:
        found = ''
    return found

# multiprocessing helpers
def split_list(alist, splits=1):
    length = len(alist)
    return [alist[i * length // splits: (i + 1) * length // splits]
            for i in range(splits)]


# path helpers
def MoveandCheck(src, dest):
    '''
    This function tries to move a file with current path "src" to a dest path "dest" and 
    checks if the src file exists and if it was copied successfully to dest
    :param src: full path of srcinal location (with (srcinal) filename in the path)
    :param dest: full path of dest location (with (new) filename in the path)
    '''
    if os.path.exists(src):
        print(f"Move {src} to {dest}")
        shutil.move(src, dest)
        if not os.path.exists(dest):
            raise ValueError(f'failed to move {src}')
        else:
            print(f'successfully moved {os.path.basename(src)} to {os.path.basename(dest)} dest location')
    else:
        raise Warning(f'file {os.path.basename(src)} does not exist in src folder!')


def getSegList(path):
    '''
    This function lists all "*_seg.mgz"-files that are in the given path. 

    :param path: path to BIDS derviatives database
    :return: return the lists of "*_seg.mgz"-files.
    '''
    seg_ls = sorted(list(Path(path).rglob('*_seg.mgz')))
    return seg_ls

def parse_pbvc_from_html_fsl(filename):
    with open(filename,'r') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    pbvc_text = str(soup.find_all('b')[5])
    assert "PBVC" in pbvc_text, 'Cannot extract pbvc from report.html, naming convention changed!'
    number = pbvc_text.split(':')[1]
    pbvc_value = float(number.split('<')[0])
    return pbvc_value

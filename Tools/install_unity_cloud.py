"""Install the verified Linux Unity 6.6 editor outside the checkout. No licence activation."""
import base64
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request

VERSION='6000.6.7f1'
URL='https://download.unity3d.com/download_unity/b22767f04f04/LinuxEditorInstaller/Unity-6000.6.7f1.tar.xz'
INTEGRITY='4MGptdBzL5X5+kDlc+Ypqg=='  # Published by Unity's official release API over HTTPS.
SIZE=4138711428
ROOT=Path('/workspace/toolchains')
DEST=ROOT/('unity-'+VERSION)
ARCHIVE=ROOT/('Unity-'+VERSION+'.tar.xz')
MARKER=ROOT/'unity-installation.json'

def verify():
    digest=hashlib.md5()
    with ARCHIVE.open('rb') as source:
        while block:=source.read(8*1024*1024):digest.update(block)
    return ARCHIVE.stat().st_size==SIZE and base64.b64encode(digest.digest()).decode()==INTEGRITY

def main():
    if (DEST/'Editor/Unity').is_file() and MARKER.exists():
        record=json.loads(MARKER.read_text())
        if record.get('version')==VERSION and record.get('verified'):
            print('Previously verified editor is retained at',DEST);return
    ROOT.mkdir(parents=True,exist_ok=True)
    if not ARCHIVE.exists() or not verify():
        with urllib.request.urlopen(URL,timeout=60) as source,ARCHIVE.open('wb') as output:
            while block:=source.read(8*1024*1024):output.write(block)
    if not verify():raise RuntimeError('Official archive checksum mismatch; archive will not be extracted')
    DEST.mkdir(parents=True,exist_ok=True)
    with tarfile.open(ARCHIVE,'r:xz') as tar:tar.extractall(DEST,filter='data')
    MARKER.write_text(json.dumps(dict(version=VERSION,url=URL,integrity='md5-'+INTEGRITY,bytes=SIZE,verified=True),indent=2)+'\n')
    print('Editor installed. Activation is a separate prerequisite.')
if __name__=='__main__':main()

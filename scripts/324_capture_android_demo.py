"""Capture local emulator demonstration screens; no model changes or publishing."""
import argparse
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--click');args=parser.parse_args()
    assert re.fullmatch('[a-z0-9_]+',args.name)
    out=ROOT/'outputs/android_demonstration_20261031_v1';out.mkdir(exist_ok=True)
    adb=ROOT/'outputs/android_toolchain/sdk/platform-tools/adb.exe'
    def call(*a):return subprocess.run([str(adb),'-s','emulator-5554',*a],capture_output=True,check=True)
    def dump():
        call('shell','uiautomator','dump','/sdcard/truehue_demo_ui.xml')
        return call('exec-out','cat','/sdcard/truehue_demo_ui.xml').stdout
    if args.click:
        nodes=[n for n in ET.fromstring(dump()).iter('node') if n.get('text')==args.click or n.get('content-desc')==args.click]
        assert len(nodes)==1,(args.click,len(nodes))
        x1,y1,x2,y2=map(int,re.findall(r'\d+',nodes[0].get('bounds')))
        call('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))
    target=out/(args.name+'.xml');assert not target.exists()
    raw=dump();target.write_bytes(raw)
    (out/(args.name+'.png')).write_bytes(call('exec-out','screencap','-p').stdout)
    sys.stdout.reconfigure(encoding='utf-8')
    for n in ET.fromstring(raw).iter('node'):
        if n.get('text') or n.get('content-desc'):print(n.get('text'),n.get('content-desc'),n.get('bounds'))


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Create a synthetic event timing signal, NEVER human narration or a soundtrack.

Each approved event selects a distinct tone. This verifies cue placement, not meaning.
The output is a new PCM16 mono 16kHz WAV. Does not overwrite existing files.
"""
import argparse
import array
import math
import sys
import wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from reelforge.contracts.project import load_project
from reelforge.unified.contract import frame


def write_fixture(request, output):
    rate=16000
    duration=request['duration_seconds']
    if type(duration) is not int or not 6<=duration<=60:
        raise ValueError('Timing fixture is limited to 6..60 seconds')
    spans=[(frame(e['start']),frame(e['end'])) for e in request['events']]
    with Path(output).open('xb') as raw, wave.open(raw,'wb') as wav:
        wav.setparams((1,2,rate,0,'NONE','not compressed'))
        for start in range(0,rate*duration,4096):
            data=array.array('h')
            for i in range(start,min(start+4096,rate*duration)):
                f=i*30//rate
                event=next(k for k,(a,b) in enumerate(spans) if a<=f<b)
                # Continuous low-amplitude carrier and a short event marker.
                tone=211+event*53
                elapsed=i-spans[event][0]*rate//30
                marker=2000*math.sin(2*math.pi*997*i/rate) if elapsed<rate//10 else 0
                value=2500*math.sin(2*math.pi*tone*i/rate)+marker
                data.append(int(value))
            if sys.byteorder!='little':data.byteswap()
            wav.writeframesraw(data.tobytes())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('request',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();write_fixture(load_project(a.request),a.output)

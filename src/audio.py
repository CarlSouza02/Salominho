"""Vinheta Salominho: OGG opcional ou WAV offline gerado pela biblioteca-padrão."""
from __future__ import annotations
from array import array
import math
from pathlib import Path
import wave

BPM = 112
RATE = 22050
BEAT = 60 / BPM
DURATION = 16 * BEAT + 3.2
NOTES = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
MELODY = [
    (0,'G5',.5),(.5,'B5',.5),(1,'D6',1),(2,'G5',.5),(2.5,'A5',.5),(3,'B5',.85),
    (4,'A5',.5),(4.5,'B5',.5),(5,'C6',1),(6,'B5',.5),(6.5,'G5',.5),(7,'A5',.9),
    (8,'B5',.5),(8.5,'A5',.5),(9,'G5',1),(10,'E5',.5),(10.5,'G5',.5),(11,'A5',.9),
    (12,'B5',.5),(12.5,'D6',.5),(13,'F#6',1),(14,'A5',.5),(14.5,'F#5',.5),(15,'G5',1.05),
]
CHORDS = [(0,['G3','D4','G4','B4']),(4,['E3','B3','E4','G4']),
          (8,['C3','G3','C4','E4']),(12,['D3','A3','D4','F#4'])]

def frequency(note: str) -> float:
    return 440 * 2 ** ((12 * (int(note[-1]) + 1) + NOTES[note[:-1]] - 69) / 12)

def render_wav(destination: Path) -> Path:
    """Cria a vinheta WAV sem numpy, scipy ou ffmpeg."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    n = int(DURATION * RATE)
    signal = array('f', [0.0]) * n

    def add(note: str, start_beat: float, beats: float, volume: float, instrument: str):
        start = int((.12 + start_beat * BEAT) * RATE)
        end = min(n, start + int((beats * BEAT + (.35 if instrument == 'harp' else .12)) * RATE))
        hz = frequency(note)
        for i in range(start, end):
            t = (i-start) / RATE
            length = (end-start) / RATE
            if instrument == 'flute':
                attack = min(1., t/.06)
                release = min(1., (length-t)/.14)
                phase = 2*math.pi*hz*(t+.0015*math.sin(2*math.pi*5*t))
                sound = math.sin(phase)+.13*math.sin(2*phase)
            elif instrument == 'harp':
                attack = min(1.,t/.008)
                release = min(1.,(length-t)/.08)
                phase = 2*math.pi*hz*t
                sound = math.sin(phase)*math.exp(-4*t)+.35*math.sin(2*phase)*math.exp(-8*t)
            else:
                attack = min(1.,t/.005)
                release = min(1.,(length-t)/.15)
                phase = 2*math.pi*hz*t
                sound = (math.sin(phase)+.22*math.sin(2.005*phase))*math.exp(-2.7*t)
            signal[i] += volume*sound*max(0.,min(attack,release))

    for beat,note,beats in MELODY:
        add(note,beat,beats,.22,'flute')
    for beat,chord in CHORDS:
        for step,which in enumerate((0,1,2,3,2,1,3,1)):
            add(chord[which],beat+step*.5,.5,.095,'harp')
        add(chord[0],beat,3.8,.10,'flute')
    for beat,note in ((1,'G6'),(5,'E6'),(9,'G6'),(13,'A6'),
                       (16,'G4'),(16.12,'B4'),(16.24,'D5'),(16.37,'G5')):
        add(note,beat,1.3 if beat<16 else 2.5,.09,'bell')
    peak = max(abs(v) for v in signal) or 1
    fade_start = int((DURATION-.75)*RATE)
    pcm = array('h')
    for i,value in enumerate(signal):
        fade = max(0.,(n-i)/max(1,n-fade_start)) if i>=fade_start else 1.
        pcm.append(round(max(-1.,min(1.,value/peak*.80*fade))*32767))
    with wave.open(str(destination),'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm.tobytes())
    return destination

def locate_music(base: Path) -> Path:
    """Prioriza OGG; sintetiza WAV local caso a faixa não esteja copiada."""
    ogg = base/'assets'/'audio'/'salominho_vinheta_v01.ogg'
    if ogg.is_file():
        return ogg
    wav = base/'cache'/'salominho_vinheta_generated.wav'
    return wav if wav.is_file() else render_wav(wav)

def play_intro(pygame_module, base: Path, volume: float=.55) -> bool:
    try:
        if not pygame_module.mixer.get_init():
            pygame_module.mixer.init()
        pygame_module.mixer.music.load(str(locate_music(base)))
        pygame_module.mixer.music.set_volume(volume)
        pygame_module.mixer.music.play(loops=0)
        return True
    except (OSError,ValueError,pygame_module.error) as exc:
        print(f'Áudio indisponível: {exc}')
        return False

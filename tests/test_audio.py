import tempfile
import unittest
import wave
from pathlib import Path
from src.audio import DURATION, RATE, frequency, locate_music, render_wav

class AudioTests(unittest.TestCase):
    def test_frequency(self):
        self.assertAlmostEqual(frequency('A4'),440.0)

    def test_generated_music_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio=render_wav(Path(tmp)/'music.wav')
            with wave.open(str(audio),'rb') as file:
                self.assertEqual(file.getframerate(),RATE)
                self.assertEqual(file.getnchannels(),1)
                self.assertAlmostEqual(file.getnframes()/RATE,DURATION,delta=.001)

    def test_prefer_ogg(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            ogg=root/'assets/audio/salominho_vinheta_v01.ogg'
            ogg.parent.mkdir(parents=True)
            ogg.write_bytes(b'test')
            self.assertEqual(locate_music(root),ogg)

if __name__=='__main__':
    unittest.main()

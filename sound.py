#!/usr/bin/env python3

import os
import queue
from playsound import playsound

class SoundThread:
    def __init__(self, queue):
        self.poll_time_ms = 1000
        self.queue = queue

        beep_wav = "beep.wav"
        silence_wav = "silence.wav"
        script_dir = os.path.dirname(os.path.realpath(__file__))

        self.beep_file = os.path.join(script_dir, beep_wav)
        self.silence_file = os.path.join(script_dir, silence_wav)

    def beep(self):
        self.queue.put("beep")

    def run(self):
        while True:
            try:
                cmd = self.queue.get(block=True, timeout=self.poll_time_ms * 1e-3)
                if cmd == "stop":
                    return
                elif cmd == "beep":
                    playsound(self.beep_file)
            except queue.Empty:
                playsound(self.silence_file)

    def stop(self):
        self.queue.put("stop")

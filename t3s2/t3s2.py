import logging
import pyttsx3 # type: ignore
import socket # type: ignore
import sys

from pygtail import Pygtail # type: ignore
from time import sleep
from keyboard import press, release # type: ignore


class Voice():
    def __init__(self, hint: str = None, rate: int = 180):
        self.engine = pyttsx3.init()

        if hint:
            # Pick the first voice that has "hint" in its ID string.
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if hint in voice.id:
                    self.engine.setProperty('voice', voice.id)
                    continue

        self.engine.setProperty('rate', rate)

    def say(self, text: str) -> None:
        """Speak the given text using the speech engine.

        Args:
            text (str): The text to say.
        """
        self.engine.say(text)
        self.engine.runAndWait()
    
    def transmit(self, text: str, ptt_key: str = 'right ctrl'):
        """Speak the given text and transmit it over SRS.

        In reality this just holds down a keyboard key in order to "key" the
        SRS microphone while speaking, then releases the key. SRS must have
        "PTT" (push to talk) bound to this key.

        Args:
            text (str): The text to transmit.
        """
        press(ptt_key)
        self.say(text)
        release(ptt_key)

# while True:
#     for line in Pygtail(dcs_log):
#         sys.stdout.write(line)
#         if 'SAY=' in line:
#             engine.say(line.split('SAY=')[-1])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('', 10259))
    listener.listen(6)

    voice = Voice("emma")

    while True:
        client_connection, client_address = listener.accept()
        payload = bytearray()
        
        while True:
            packet = client_connection.recv(1500)
            if not packet:
                client_connection.close()
                break
            payload.extend(packet)
        
        if payload:
            text = payload.decode()
            logging.info(f'text={text}')
            voice.transmit(text)
            sleep(0.1)
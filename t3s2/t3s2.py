import logging
import pyttsx3  # type: ignore
import socket  # type: ignore
import re

from time import sleep
from keyboard import press, release  # type: ignore


def translate(text):
    text = text.replace('.00', '')

    # Use correct phonetic for decimal numbers.
    decimal_re = re.compile(r'(\d)[.](\d)')
    text = decimal_re.sub(r'\1 decimal \2', text)

    # Rework bullseye coordinate calls.
    bullseye_re = re.compile(r'bullseye (\d+) for (\d+) at (\d+)')
    text = bullseye_re.sub(r'bullseye \1. range \2. altitude \3.', text)

    # Put spaces between numerals so that the voice will say "one five" not
    # "fifteen".
    for num in [str(n) for n in range(10)]:
        text = text.replace(num, f'{num} ')

    text = text.replace(' 9 ', ' niner ')

    text = text.replace(' gnd ', ' ground ')
    text = text.replace('RPG', 'ah-peejee')
    text = text.replace('LZ', 'ell-zee')
    text = text.replace('Fly heading', 'Flyheading')

    text = text.replace(' medevac ', ' meddivack ')
    text = text.replace('KHz', 'kilohertz')
    text = text.replace('MHz', 'megahertz')

    logging.info(f"Tranlated: {text}")
    return text


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
        logging.info(f"Say: {text}")
        self.engine.say(translate(text))
        self.engine.runAndWait()

    def transmit(self, text: str, ptt_key: str = r'right ctrl'):
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('', 10259))
    listener.listen(6)

    voice = Voice("amy", rate=140)

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
            logging.info(f'Payload: {text}')
            voice.transmit(text)
            sleep(0.1)

# RTP Voice Chat Application
# This implementation demonstrates RTP protocol for real-time voice communication

import socket
import threading
import struct
import time
import pyaudio
import random


class RTPPacket:
    """RTP Packet structure according to RFC 3550"""

    def __init__(self, version=2, padding=0, extension=0, cc=0, marker=0,
               payload_type=0, sequence_number=0, timestamp=0, ssrc=0, payload=b''):
        self.version = version
        self.padding = padding
        self.extension = extension
        self.cc = cc
        self.marker = marker
        self.payload_type = payload_type
        self.sequence_number = sequence_number
        self.timestamp = timestamp
        self.ssrc = ssrc
        self.payload = payload

    def pack(self):
        """Pack RTP packet into bytes"""
        # First 32 bits: V(2), P(1), X(1), CC(4), M(1), PT(7), Sequence Number(16)
        first_word = (self.version << 30) | (self.padding << 29) | (self.extension << 28) | \
                     (self.cc << 24) | (self.marker << 23) | (self.payload_type << 16) | \
                     self.sequence_number

        # Pack header (12 bytes minimum)
        header = struct.pack('!III', first_word, self.timestamp, self.ssrc)

        return header + self.payload

    @classmethod
    def unpack(cls, data):
        """Unpack RTP packet from bytes"""
        if len(data) < 12:
            return None

        # Unpack header
        first_word, timestamp, ssrc = struct.unpack('!III', data[:12])

        # Extract fields from first word
        version = (first_word >> 30) & 0x3
        padding = (first_word >> 29) & 0x1
        extension = (first_word >> 28) & 0x1
        cc = (first_word >> 24) & 0xF
        marker = (first_word >> 23) & 0x1
        payload_type = (first_word >> 16) & 0x7F
        sequence_number = first_word & 0xFFFF

        payload = data[12:]

        return cls(version, padding, extension, cc, marker, payload_type,
                   sequence_number, timestamp, ssrc, payload)


class RTPVoiceChat:
    """RTP Voice Chat Client"""

    def __init__(self, local_port=5004, remote_host='127.0.0.1', remote_port=5005):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port

        # Audio configuration
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 8000

        # RTP configuration
        self.sequence_number = random.randint(0, 65535)
        self.timestamp = 0
        self.ssrc = random.randint(0, 0xFFFFFFFF)

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Create UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.local_port))

        self.running = False

    def start_stream(self):
        """Initialize audio streams"""
        # Input stream (microphone)
        self.input_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        # Output stream (speakers)
        self.output_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )

    def send_audio(self):
        """Send audio data using RTP"""
        print("Started sending audio...")

        while self.running:
            try:
                # Read audio data from microphone
                audio_data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)

                # Create RTP packet
                rtp_packet = RTPPacket(
                    payload_type=0,  # PCMU (G.711 μ-law)
                    sequence_number=self.sequence_number,
                    timestamp=self.timestamp,
                    ssrc=self.ssrc,
                    payload=audio_data
                )

                # Send RTP packet
                packet_data = rtp_packet.pack()
                self.socket.sendto(packet_data, (self.remote_host, self.remote_port))

                # Update sequence number and timestamp
                self.sequence_number = (self.sequence_number + 1) % 65536
                self.timestamp += self.CHUNK

                time.sleep(0.02)  # ~50 packets per second

            except Exception as e:
                print(f"Error sending audio: {e}")
                break

    def receive_audio(self):
        """Receive and play audio data using RTP"""
        print("Started receiving audio...")

        while self.running:
            try:
                # Receive RTP packet
                data, addr = self.socket.recvfrom(8192)

                # Unpack RTP packet
                rtp_packet = RTPPacket.unpack(data)

                if rtp_packet:
                    # Play audio data
                    self.output_stream.write(rtp_packet.payload)

            except Exception as e:
                print(f"Error receiving audio: {e}")
                break

    def start_chat(self):
        """Start voice chat"""
        print(f"Starting RTP Voice Chat...")
        print(f"Local port: {self.local_port}")
        print(f"Remote: {self.remote_host}:{self.remote_port}")
        print("Press 'q' and Enter to quit")

        self.running = True
        self.start_stream()

        # Start threads for sending and receiving
        send_thread = threading.Thread(target=self.send_audio)
        receive_thread = threading.Thread(target=self.receive_audio)

        send_thread.daemon = True
        receive_thread.daemon = True

        send_thread.start()
        receive_thread.start()

        # Wait for user input to quit
        while True:
            user_input = input()
            if user_input.lower() == 'q':
                break

        self.stop_chat()

    def stop_chat(self):
        """Stop voice chat and cleanup"""
        print("Stopping voice chat...")
        self.running = False

        # Close audio streams
        if hasattr(self, 'input_stream'):
            self.input_stream.stop_stream()
            self.input_stream.close()

        if hasattr(self, 'output_stream'):
            self.output_stream.stop_stream()
            self.output_stream.close()

        self.audio.terminate()
        self.socket.close()
        print("Voice chat stopped.")


def main():
    """Main function to run the application"""
    print("RTP Voice Chat Application")
    print("=" * 30)

    # Get configuration from user
    print("\nConfiguration:")
    local_port = input("Enter local port (default 5004): ").strip()
    local_port = int(local_port) if local_port else 5004

    remote_host = input("Enter remote host (default 127.0.0.1): ").strip()
    remote_host = remote_host if remote_host else '127.0.0.1'

    remote_port = input("Enter remote port (default 5005): ").strip()
    remote_port = int(remote_port) if remote_port else 5005

    # Create and start voice chat
    try:
        voice_chat = RTPVoiceChat(local_port, remote_host, remote_port)
        voice_chat.start_chat()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()



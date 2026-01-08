# CN RTP Voice Chat Project

This project implements a **Real-Time Voice Chat application** using **RTP (Real-Time Transport Protocol)** over **UDP** in **Python**.  
It demonstrates how real-time audio communication works at the transport layer using packet-based transmission.

---

##  Project Overview
The application captures live audio from the microphone, encapsulates it into RTP packets, and transmits it over a UDP socket to another endpoint.  
At the receiver side, RTP packets are decoded and played back in real time.

This project is designed as part of a **Computer Networks (CN)** practical to understand real-time communication protocols.

---

##  Features
- Real-time voice communication
- RTP packet implementation (sequence number, timestamp, SSRC)
- UDP-based data transmission
- Audio capture and playback using PyAudio
- Multithreaded sending and receiving
- Simple command-line interface

---

##  Concepts Covered
- Real-Time Transport Protocol (RTP)
- User Datagram Protocol (UDP)
- Socket programming in Python
- Ports and local/remote communication
- Audio streaming fundamentals
- Client-to-client communication model

---

##  Requirements
- Python 3.9 or 3.10
- PyAudio library
- Working microphone and speakers/headphones
- Windows / Linux / macOS (tested on Windows)

---

##  How to Run the Project
1. Open **two terminals / command prompts**
2. Navigate to the project folder
3. Run the program in both terminals:

### Terminal 1
- Local port: `5004`
- Remote port: `5005`

### Terminal 2
- Local port: `5005`
- Remote port: `5004`

4. Start speaking into the microphone  
5. Press `q` to stop the application

---



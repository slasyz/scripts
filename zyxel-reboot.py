#!/usr/bin/python3

import getpass
import telnetlib
import time

HOST = "192.168.1.1"
USER = "admin"
PASSWORD = "7TIc5RGf"

print("Connecting...")
tn = telnetlib.Telnet(HOST)

print("Sending login...")
tn.read_until(b"Login: ")
tn.write(USER.encode('ascii') + b"\n")

if PASSWORD:
    print("Sending password...")
    tn.read_until(b"Password: ")
    tn.write(PASSWORD.encode('ascii') + b"\n")

print("Sending \"sys reboot\" command.")
tn.write(b"sys reboot\n")
time.sleep(1)

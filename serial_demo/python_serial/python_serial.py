import sys
import serial.tools.list_ports
import serial

# connect to the open serial port
ports = list(serial.tools.list_ports.comports())
ports = [p[0] for p in ports]
if len(ports) == 0:
    print("couldn't find any open ports")
    exit()
# ser = serial.Serial(ports[0], 115200, timeout=0.1)
ser = serial.Serial(ports[0], 230400, timeout=0.1)


import markovify
corpus = ""
with open("harry_potter.txt", encoding="ascii", errors='ignore') as f:
    corpus += "\n" + f.read()
text_model = markovify.Text(corpus)
# try to generate a weird sentence
def make_message():
    # return text_model.make_short_sentence(40, tries=100)+'\n'
    # return text_model.make_short_sentence(97, tries=10)+'\n'
    # return text_model.make_short_sentence(30, tries=100)+'\n'
    return text_model.make_sentence()+'\n'


# default message to send
message = "Love"

# take input arguments if they are given
args = sys.argv[1:]
if len(args) >= 1:
    message = " ".join(args[0:])
else:

    message = make_message()

    # send the initial string
    to_write = bytearray(message.encode("ascii"))
    ser.write(to_write)

    message = make_message()

    # send a new string when it's done showing the old one
    while True:
        while ser.in_waiting:
            ser.readline()  # clear out the buffer
            print("it requested a message!")
            # message = text_model.make_short_sentence(40, tries=100)
            to_write = bytearray(message.encode("ascii"))
            ser.write(to_write)
            print("we replied!")
            message = make_message()

# send the string
to_write = bytearray(message.encode("ascii"))
ser.write(to_write)

import sys
import serial.tools.list_ports
import serial

# connect to the open serial port
ports = list(serial.tools.list_ports.comports())
ports = [p[0] for p in ports]
if len(ports) == 0:
    print("couldn't find any open ports")
    exit()
ser = serial.Serial(ports[0], 115200)


# default message to send
message = "default text"

# take input arguments if they are given
args = sys.argv[1:]
if len(args) >= 1:
    message = " ".join(args[0:])
else:

    # try to generate a weird sentence
    import markovify
    corpus = ""
    with open("harry_potter.txt", encoding="ascii", errors='ignore') as f:
        corpus += "\n" + f.read()
    text_model = markovify.Text(corpus)
    # message = text_model.make_short_sentence(97, tries=10)
    message = text_model.make_sentence()


# send the string
to_write = bytearray(message.encode("ascii"))
ser.write(to_write)

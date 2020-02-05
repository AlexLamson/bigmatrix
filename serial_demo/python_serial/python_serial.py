import os
import sys
import serial.tools.list_ports as list_ports
from serial import Serial
import re
from time import sleep
import markovify
from collections.abc import Iterable

enable_audio = False

# connect to the open serial port
ports = list(list_ports.comports())
ports = [p[0] for p in ports]
if len(ports) == 0:
    print("couldn't find any open ports")
    exit()
# ser = Serial(ports[0], 115200, timeout=0.1)
ser = Serial(ports[0], 230400, timeout=0.1)


# default message to send
message = "Love"

# take input arguments if they are given
args = sys.argv[1:]
args = [x.split() if ' ' in x else x for x in args]

def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el
args = list(flatten(args))


# figure out how long it should be shown
duration = 0  # seconds

if len(args) >= 1:
    if re.match(r'\d+(\.\d+)?s', args[0]) is not None:
        duration = float(args[0][:-1])
        args = args[1:]

    message = " ".join(args)+" "
else:


    # import os
    # books = os.listdir("orson_scott_card")


    forbidden_chars = '()"\'[]'

    state_size = 2  # default is 2
    # books = "beatles".split()
    # books = "spiderman".split()
    # books = "das_boot".split()
    # books = "dune".split()
    # books = "fpt".split()
    # books = "bee_movie".split()
    # books = "django_unchained".split()
    # books = "anchorman".split()
    books = "hhgttg".split()
    # books = "harry_potter slaughterhouse_five hhgttg".split()
    # books = "harry_potter 1984 slaughterhouse_five hhgttg".split()
    # books = "harry_potter game_of_thrones enders_game 1984 dune neuromancer slaughterhouse_five snow_crash hhgttg foundation enders_shadow".split()
    # books = "enders_game 1984 slaughterhouse_five hhgttg foundation enders_shadow".split()
    models = []
    for book in books:
        print("reading {}".format( book.replace("_", " ") ))
        # with open("orson_scott_card/"+book, encoding="ascii", errors='ignore') as f:
        with open("books/"+book+".txt", encoding="ascii", errors='ignore') as f:
            book_text = f.read()
            book_text = "".join([x for x in book_text if x not in forbidden_chars])
        new_model = markovify.Text(book_text, state_size=state_size)
        models += [new_model]

    print("merging all books together")
    text_model = markovify.combine(models, [1 for x in range(len(models)) ])


    # try to generate a weird sentence
    def make_message():
        # return text_model.make_short_sentence(30, tries=100)
        # return text_model.make_short_sentence(40, tries=100)
        # return text_model.make_short_sentence(97, tries=10)
        return text_model.make_short_sentence(128, tries=100)
        # return text_model.make_sentence()



    message = make_message()
    print(message)

    # send the initial string
    to_write = bytearray(message.encode("ascii"))
    ser.write(to_write)
    if enable_audio:
        os.system("say '{}'".format(message))

    message = make_message()
    # print(message)

    # send a new string when it's done showing the old one
    while True:
        while ser.in_waiting:
            ser.readline()  # clear out the buffer
            # print("it requested a message!")
            # message = text_model.make_short_sentence(40, tries=100)
            print(message)
            to_write = bytearray((message+'\n').encode("ascii"))
            ser.write(to_write)
            if enable_audio:
                os.system("say '{}' > /dev/null 2>&1".format(message))
            # print("we replied!")
            message = make_message()
            if not enable_audio:
                sleep(0.5)
        sleep(0.05)

# send the string
to_write = bytearray((message+" \n").encode("ascii"))
ser.write(to_write)

# clear the matrix after `duration` seconds, if it was specified
if duration > 0:
    sleep(duration)
    to_write = bytearray(("  \n").encode("ascii"))
    ser.write(to_write)


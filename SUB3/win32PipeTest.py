#we wanna test win32
import time
import sys
import win32pipe, win32file, pywintypes
import struct


def pipe_server():
    print("pipe server")
    count = 0
    #C++ client example reads from Foo; this writes to Foo
    pipe = win32pipe.CreateNamedPipe(
        r'\\.\\pipe\\Foo',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
    try:
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")

        while count < 10:
            print(f"writing message {count}")
            send_message(pipe, count)
            time.sleep(1)
            count += 1

        print("finished now")
    finally:
        win32file.CloseHandle(pipe)

def send_message(pipe, words):
    # convert to bytes and write string to pipe
    #some_data = str.encode(f"{words}") #encodes variable words into an fstring, didn't help
    #other_data = bytes(chr(words).encode('utf-8')) #didn't help us
    #chop num into digits
    some_data = struct.pack('P', words) #encodes to ascii bytes C can read (7 is a bell sound!!!!!!!!!!!)
    win32file.WriteFile(pipe, some_data)





def pipe_client():
    print("pipe client")
    quit = False

    while not quit:
        try:
            #C++ server writes to Fan
            #this reads from Fan
            handle = win32file.CreateFile(
                r'\\.\\pipe\\Fan',
                win32file.GENERIC_READ,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            print("res time")
            res = 1 #win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_BYTE, None, None)
            #if the above function is called while interacting with C, the function hangs!
            #this is because the C side makes a ONE WAY pipe, which python does not have permission to edit.
            #solution: make it correctly on the C side.
            print("res done")
            #PIPE_READMODE_MESSAGE OR PIPE_READMODE_BYTE^
            if res == 0:
                print(f"SetNamedPipeHandleState return code: {res}")
            while True:
                resp = win32file.ReadFile(handle, 64*1024)[1].decode('ascii')
                print(f"message: {resp}")
        except pywintypes.error as e:
            if e.args[0] == 2:
                print("no pipe, trying again in a sec")
                time.sleep(1)
            elif e.args[0] == 109:
                print("broken pipe, bye bye")
                quit = True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("need s or c as argument")
    elif sys.argv[1] == "s":
        pipe_server()
    elif sys.argv[1] == "c":
        pipe_client()
    else:
        print(f"no can do: {sys.argv[1]}")
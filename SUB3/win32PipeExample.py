#we wanna test win32
import time
import sys
import win32pipe, win32file, pywintypes


#This is an example pipe file! 
# It is not integral to the project, but it's a good test for communication between python and C++
#(or any other programming language which can use windows pipes)
#this is an example of pipes, in case you ever need to troubleshoot them.
#pipes are a method of communication between processes in windows.
#functions read and write to pipes almost (but not quite) like they are a file.
#if you write to a pipe without reading from it, a process may hang.
#if you read to a pipe that hasn't been written to, you may have an error.
#C++ gets weird about data types, but the python end is intuitive once you practice.

def pipe_server():
    print("pipe server")
    count = 0
    #create a pipe handle at address ...Foo
    #there is documentation of what each flag means technically; this is win32 api documentation, not C++ or py.
    pipe = win32pipe.CreateNamedPipe(
        r'\\.\pipe\Foo',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
    try:
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None) 
        #this process connects to the location your pipe handle points to. It waits for the client to connect.
        print("got client")

        while count < 10:
            print(f"writing message {count}")
            # convert to bytes
            some_data = str.encode(f"{count}")
            win32file.WriteFile(pipe, some_data) #writeFile is good enough to send some_data to the pipe.
            time.sleep(1)
            count += 1

        print("finished now")
    finally:
        win32file.CloseHandle(pipe) #always clean up after yourself.


def pipe_client():
    print("pipe client")
    quit = False

    while not quit:
        try:
            #the client also makes a pipe handle! This end is treated like a file.
            #the client wants to open an existing pipe.
            handle = win32file.CreateFile(
                r'\\.\pipe\Foo',
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            if res == 0:
                print(f"SetNamedPipeHandleState return code: {res}")
            while True:
                resp = win32file.ReadFile(handle, 64*1024) #you don't want to read from a pipe that isn't there
                print(f"message: {resp}")
        except pywintypes.error as e:
            if e.args[0] == 2:
                print("no pipe, trying again in a sec") #catches 'no pipe' error (else it would crash)
                time.sleep(1)
            elif e.args[0] == 109:
                print("broken pipe, bye bye")
                quit = True


if __name__ == '__main__':
    #to run, you want to run it like a normal python program; ...Example.py s or ...Example.py c.
    #play around and get a feel for it.
    if len(sys.argv) < 2:
        print("need s or c as argument")
    elif sys.argv[1] == "s":
        pipe_server()
    elif sys.argv[1] == "c":
        pipe_client()
    else:
        print(f"no can do: {sys.argv[1]}")
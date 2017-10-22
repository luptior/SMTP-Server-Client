# A serve program of SMTP

import sys,os

from socket import *

"""helper functions from previous SMTP hw"""

def ifmailfromcmd(str):

    if str[0] != "M":
        return False

    # check "MAIL FROM:"
    if len(str) < len("MAIL FROM:"):
        return False

    if str[0:4] != "MAIL":
        return False

    i = 4
    # check the <nullspace> after MAIL whose len is 4
    for char in str[4:]:
        if not ifsp(char):
            break
        else:
            i += 1

    if str[i:i + 5] != "FROM:" or i == 4:
        return False

    i += 5
    # check the <nullspace> after FROM: whose len is 5
    for char in str[i:]:
        if not ifsp(char):
            break
        else:
            i += 1
    # i is the start place of path

    # check the reversepath
    if ifsp(str[-1]):
        ii = -1
        while ifsp(str[ii]):
            ii -= 1
        return ifreversepath(str[i:ii + 1])
    elif str[-1] == ">":
        return ifreversepath(str[i:])
    else:
        ii = 1
        while str[-ii] != ">" and ii <= len(str) - 9:
            ii += 1
        if ii > 1 and ii != len(str) - 8:
            return False
        else:
            return ifreversepath(str[i:])


def ifreversepath(str):
    if len(str) < len("<1@123>"):
        return False
    return ifpath(str)


def ifdatacmd(str):

    if str[0] == "D":
        if str[0:4] != "DATA":
            return False
        else:
            for char in str[4:]:
                if not ifsp(char):
                    return False
            return True
    else:
        return False


def ifrcpttocmd(str):

    if str[0] != "R" :
        return False

    # check "RCPT TO:"
    if len(str) < len("RCPT TO:"):
        return False

    if str[0:4] != "RCPT":
        return False

    i = 4
    # check the <nullspace>
    for char in str[4:]:
        if not ifsp(char):
            break
        else:
            i += 1

    if str[i:i + 3] != "TO:" or i == 4:
        return False

    i += 3
    # check the <nullspace>
    for char in str[i:]:
        if not ifsp(char):
            break
        else:
            i += 1
    # i is the start place of path

    # check the forwardpath
    if ifsp(str[-1]):
        ii = -1
        while ifsp(str[ii]):
            ii -= 1
        return ifforwardpath(str[i:ii + 1])
    elif str[-1] == ">":
        return ifforwardpath(str[i:])
    else:
        ii = 1
        while str[-ii] != ">" and ii <= len(str) - 9:
            ii += 1
        if ii > 1 and ii != len(str) - 8:
            return False
        else:
            return ifforwardpath(str[i:])


def ifforwardpath(str):
    if len(str) < len("<1@123>"):
        return False
    return ifpath(str)


def ifpath(str):
    if not (str[0] == "<" and str[-1] == ">") or str[-2] == " ":
        return False
    else:
        return ifmailbox(str[1:-1])


def ifmailbox(str):
    # check if there is a "@"
    i = 0
    for char in str:
        if char == "@":
            break
        i += 1
    # i is the index of the str
    if i == 0:
        # in the str, i = 0, the first char is "@"
        return False
    elif i == len(str) - 1:
        #  i = strlen -1 the last is "@" wrong
        return False
    elif i == len(str):
        # no "@" in the domain part
        return False
    else:
        # check the part before "@" is element and recursively check the later part ifdomain()
        return iflocalpart(str[0:i]) and ifdomain(str[i + 1:])


def ifdomain(str):
    # check if there is a "."
    i = 0
    for char in str:
        if char == ".":
            break
        i += 1
    if i == 0:
        return False
    elif i == len(str):  # . at the beginning or the end
        if str[-1] == ".":
            return False
        else:
            return ifelement(str)
    else:
        if not ifelement(str[0:i]):
            return False
        else:
            return ifdomain(str[i + 1:])


def ifelement(str):
    if len(str) < 2:
        return False
    elif ifname(str):
        return True
    else:
        return False


def iflocalpart(str):
    if not ifc(str[0]):
        return False
    elif ifstring(str):
        return True
    else:
        return False


def ifname(str):
    if not ifa(str[0]):
        return False
    else:
        return ifletdigstr(str)


def ifletdigstr(str):
    for char in str:
        if not ifletdig(char):
            return False
    return True


def ifletdig(char):
    if not ((ifa(char) or ifd(char))):
        return False
    else:
        return True


def ifstring(str):
    for char in str:
        if not ifc(char):
            return False
    return True


def ifCRLF(char):
    if char == "\n":
        return True
    else:
        return False


def ifsp(char):
    if ord(char) == 9 or ord(char) == 32:  # acsii value of space and tab
        return True
    else:
        return False


def ifa(char):
    if 64 < ord(char) < 91 or 96 < ord(char) < 123: # acsii value for english characters
        return True
    else:
        return False


def ifc(char):
    if ifsp(char) or ifspecial(char):
        return False
    elif ord(char) >= 0 and ord(char) <= 127:
        return True
    else:
        return False


def ifd(char):
    if 48 <= ord(char) <= 57:
        return True
    else:
        return False


def ifspecial(char):

    spchar = ["<",  ">",  "(", ")", "[", "]", " \ ",  ".",  ",",  ";",  ":", "@",  ' " ']

    if char in spchar:
        return True
    else:
        return False


def getpath(str):
    i = 0
    path_start = 0
    path_end = 0
    for char in str:
        if char == "<":
            # changed here to store in file named by domain
            path_start = i+1
            i += 1
        elif char == ">":
            path_end = i
            i += 1
        else:
            i += 1
    return str[path_start:path_end]

def getdomain(str):
    i = 0
    path_start = 0
    path_end = 0
    for char in str:
        if char == "@":
            # changed here to store in file named by domain
            path_start = i+1
            i += 1
        elif char == ">":
            path_end = i
            i += 1
        else:
            i += 1
    return str[path_start:path_end]

""" main client function starts here """


def main():
    serverPort = sys.argv[1]
    # take in the single command line arg, portnum

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', int(serverPort)))
    serverSocket.listen(1)
    # bind the socket to the serverPort


    while True:
        # whileloop #1, each loop is for a connection

        connectionSocket, addr = serverSocket.accept()
        # establish connection

        # send greeting
        connectionSocket.send(("220 %s" % gethostname()).encode())

        # waiting for SMTP HELO cmd from client and give acknowledge back
        hmsg = connectionSocket.recv(1024).decode()
        if hmsg[0:4] == "HELO" and ifdomain(hmsg[4:].strip("\n").strip()):
            # check if valid helo msg
            connectionSocket.send(("250 OK\n"+ hmsg[4:].strip("\n").strip() + " pleased to meet you.").encode())
            # send ack back
        else:
            print "HELO msg error"
            connectionSocket.close()
            continue

        # cmdcounter =1 for MAIL FROM, 2 for RCPT TO, >2 for RCPT or DATA,
        # 0 for DATA for input which indicates
        # the state of main function. The default is 1, makes the program waiting
        #  for MAIL FROM command at the first
        cmdcounter = 1
        RCPT = []
        data = ""

        while True:
            # whileloop #2, each loop is for a msg received
            cmd = connectionSocket.recv(1024).decode()

            try:
                    if cmd == "\n":
                        # store blank line
                        data += "\n"
                        continue

                    # if not blank line, strip the newline
                    cmd = cmd.strip("\n").strip()

                    if cmd == "QUIT":
                        # if receives quit, jump out of loop #2
                        break

                    if cmdcounter != 0 and cmd[0] not in ["M", "R", "D"]:
                        # get rid of uncategorized commands first
                        connectionSocket.send("500 Syntax error: command unrecognized".encode())
                        break

                    # check for the end of cmd, if meet, store all info into forward/domain files and reset
                    if cmd == ".":
                        connectionSocket.send("250 OK".encode())
                        for i in xrange(len(RCPT)):
                            filepath = "./forward/" + getdomain(RCPT[i])
                            with open(filepath, "a") as myfile:
                                    myfile.write(data[0:-2])
                        cmdcounter = 1
                        RCPT = []
                        data = ""
                        continue

                    if cmdcounter == 0:
                        # take in data state, no need to 250
                        data += cmd + "\n"
                        if cmd.split("\n")[-1] == ".":
                            connectionSocket.send("250 OK".encode())
                            for i in xrange(len(RCPT)):
                                filepath = "./forward/" + getdomain(RCPT[i])
                                with open(filepath, "a") as myfile:
                                    myfile.write(data[0:-2])
                            cmdcounter = 1
                            RCPT = []
                            data = ""
                        continue
                    elif cmdcounter == 1:
                        # take in MAIL FROM command state
                        cmd =cmd.strip()
                        if ifmailfromcmd(cmd):
                            connectionSocket.send("250 OK".encode())
                            data += "From: <"+getpath(cmd)+">\n"
                            cmdcounter += 1
                            continue
                        elif ifrcpttocmd(cmd) or ifdatacmd(cmd):
                            connectionSocket.send("503 Bad sequence of commands".encode())
                            break
                        else:
                            connectionSocket.send("500 Syntax error: command unrecognized".encode())
                            break
                    elif cmdcounter == 2:
                        cmd = cmd.strip()
                        #take in RCPT command state
                        if ifmailfromcmd(cmd) or ifdatacmd(cmd):
                            connectionSocket.send("503 Bad sequence of commands".encode())
                            break
                        elif ifrcpttocmd(cmd):
                            connectionSocket.send("250 OK".encode())
                            RCPT.append(cmd)
                            data += "To: <" + getpath(cmd) + ">\n"
                            cmdcounter += 1
                            continue
                        else:
                            print cmd
                            connectionSocket.send("500 Syntax error: command unrecognized".encode())
                            break
                    elif cmdcounter > 2:
                        cmd = cmd.strip()
                        #take in RCPT/Data command state
                        if ifmailfromcmd(cmd):
                            connectionSocket.send("503 Bad sequence of commands".encode())
                            break
                        elif ifrcpttocmd(cmd):
                            connectionSocket.send("250 OK".encode())
                            RCPT.append(cmd)
                            data += "To: <" + getpath(cmd) + ">\n"
                            cmdcounter += 1
                            continue
                        elif ifdatacmd(cmd):
                            connectionSocket.send("354 Start mail input; end with <CRLF>.<CRLF>".encode())
                            cmdcounter = 0
                            continue
                        else:
                            print cmd
                            connectionSocket.send("500 Syntax error: command unrecognized".encode())
                            break
            except IndexError:
                break
                # break loop #2 for msg received
            except EOFError:
                print "End of File error"
                break
                # break loop #2 for msg received
        connectionSocket.close()



if __name__ == "__main__":
    main()

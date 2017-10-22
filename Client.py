# A client program of SMTP


import sys

from socket import *

"""helper functions from previous SMTP hw"""

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
        print "501 Syntax error in parameters or arguments"
        return False
    elif i == len(str) - 1:
        #  i = strlen -1 the last is "@" wrong
        print "501 Syntax error in parameters or arguments"
        return False
    elif i == len(str):
        # no "@" in the domain part
        print "501 Syntax error in parameters or arguments"
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
        print "501 Syntax error in parameters or arguments"
        return False
    elif i == len(str):  # . at the beginning or the end
        if str[-1] == ".":
            print "501 Syntax error in parameters or arguments"
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
        print "501 Syntax error in parameters or arguments"
        return False
    elif ifname(str):
        return True
    else:
        print "501 Syntax error in parameters or arguments"
        return False


def iflocalpart(str):
    if not ifc(str[0]):
        print "501 Syntax error in parameters or arguments"
        return False
    elif ifstring(str):
        return True
    else:
        print "501 Syntax error in parameters or arguments"
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


""" main client function starts here """


def main():

    """take in user input"""
    try:
        # wait for mail from cmd
        switch_mf = True
        while switch_mf:
            mfcmd = raw_input("From:").strip()
            if ifmailbox(mfcmd):
                # verify the mail from cmd, if true continue to next step,
                # if false, waiting for re input
                switch_mf = False
            else:
                continue

        # wait for rcpt to cmd
        switch_rt = True
        while switch_rt:
            rtcmd = raw_input("To:")
            rpt_list_pre = rtcmd.split(",")
            # receive all the rcpt to address in single line seperated by comma,
            # then store them in list rpt_list

            rpt_list = []

            for i in rpt_list_pre:
                rpt_list.append(i.strip())

            switch_rt = False
            # default situation is all address we received is valid
            for i in rpt_list:
                if not ifmailbox(i):
                    switch_rt = True
                # check each one of forward-path, one error cause the whole loop to rerun

        # wait for subject input
        subject = raw_input("Subject:")

        # wait for msg input
        msg = []
        print "Message:".strip("/n")
        while True:
            line = raw_input()
            if line == ".":
                # if period is encountered, exit the input step
                break
            else:
                msg.append(line)
                # store each line as a element in the list msg

    except EOFError:
        # exit when end of file error is met
        sys.exit()

    # takes two command line arguments, hostname is the domain name of the server this client using
    # portname specifies the port number on which the SMTP  server is listening to the connection
    # after the user enterred a valid emil message
    serverName = sys.argv[1]
    serverPort = sys.argv[2]

    if not ifdomain(serverName):
        # check the validility of serverName
        print "Error -- wrong hostname"
        sys.exit()

    # send request to server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, int(serverPort)))

    # receive greeting message
    greeting = clientSocket.recv(1024).decode()

    # and send HELO message
    # clientSocket.send(("HELO %s\n" % serverName).encode())
    clientSocket.send(("HELO %s" % gethostname()).encode())

    # receive ack msg

    ack = clientSocket.recv(1024).decode()
    if not ack[0:3] == "250" :
        print "Error -- bad connection"
        sys.exit()


    # send everything in a single package

    # send mail from
    cmd_st = "MAIL FROM: <%s>\n" % mfcmd
    clientSocket.send(cmd_st.encode())
    # received 250 for mail from
    reply = clientSocket.recv(1024).decode()
    if not reply[0:3] == "250":
        print reply
        sys.exit()

    # send rcpt to
    for i in rpt_list:
        cmd_st =  "RCPT TO: <%s>\n" % i
        clientSocket.send(cmd_st.encode())
        # received 250 for RCPT
        reply = clientSocket.recv(1024).decode()
        if not reply[0:3] == "250":
            print reply
            sys.exit()

    # send DATA
    cmd_st = "DATA\n"
    clientSocket.send(cmd_st.encode())
    # received 354 for data
    reply = clientSocket.recv(1024).decode()
    if not reply[0:3] == "354":
        print reply
        sys.exit()

    data = "From: <%s>\n" % mfcmd
    for i in rpt_list:
        data += ("To: <%s>\n" % i)
    data += ("Subject: " + subject + "\n\n")
    for i in msg:
        data += (i+"\n")
    data += ".\n"

    clientSocket.send(data.encode())
    # received 250 for data sent
    reply = clientSocket.recv(1024).decode()
    if not reply[0:3] == "250":
        print reply
        sys.exit()
    else:
        clientSocket.send("QUIT".encode())


    # send the message and close the connection, exit program
    # clientSocket.send(data.encode())

    clientSocket.close()
    sys.exit()


if __name__ == "__main__":
    main()
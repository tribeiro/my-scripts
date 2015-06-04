#!/usr/bin/env python

################################################################################

__author__ = 'Ribeiro, T.'

################################################################################

import sys
import os
import time
import telnetlib

################################################################################

class ChimeraWatcher():

    ############################################################################

    def __init__(self):

        self.chimeralog = os.path.expanduser('~/.chimera/chimera.log')
        self.sleep = 30

        self.binary='/usr/local/bin/telegram-cli'
        self.keyfile=os.path.expanduser('~/.telegram/cwatcher.pub')
        self.logs=os.path.expanduser('~/.telegram/cwatcher.log')
        self.quiet=False

        self.ip='127.0.0.1'
        self.port=9999
        self.timeout=60

    ############################################################################

    def run(self):

        fp = open(self.chimeralog,'r')

        # Go to the end of the file
        fp.seek(0,2)

        pos = fp.tell()

        fp.close()

        try:
            while True:

                print 'Sleeping...'
                # self.t.write('msg Tiago_Ribeiro Sleeping...')
                # if self.t.expect(['SUCCESS'], timeout=5)[1]:
                #     print 'SUCCESS'
                # else:
                #     print 'TIMEOUT'

                time.sleep(self.sleep)

                print 'Waking up...'
                self.t = telnetlib.Telnet(self.ip, self.port, self.timeout)
                print 'Going Online...'
                self.t.write('status_online \r\n')
                if self.t.expect(['SUCCESS'], timeout=5)[1]:
                    print 'SUCCESS'
                else:
                    print 'TIMEOUT'

                # self.t.write('msg Tiago_Ribeiro Waking up...\r\n')
                # if self.t.expect(['SUCCESS'], timeout=5)[1]:
                #     print 'SUCCESS'
                # else:
                #     print 'TIMEOUT'
                #
                # continue

                fp = open(self.chimeralog,'r')

                # Go to the previous position in the file
                fp.seek(pos)

                for line in fp.readlines():
                    if not 'DEBUG' in line and not 'INFO' in line:
                        print line[:-1]
                        self.t.write('msg Tiago_Ribeiro %s \r\n'%(line[:-1]))
                        if self.t.expect(['SUCCESS'], timeout=5)[1]:
                            print 'SUCCESS'
                        else:
                            print 'TIMEOUT'


                # if len(msg) > 0:
                #     print msg
                #     self.t.write('msg Tiago_Ribeiro %s \r\n'%(msg))
                #     if self.t.expect(['SUCCESS'], timeout=5)[1]:
                #         print 'SUCCESS'
                #     else:
                #         print 'TIMEOUT'
                # else:
                #     self.t.write('msg Tiago_Ribeiro No events to report... \r\n')
                #     if self.t.expect(['SUCCESS'], timeout=5)[1]:
                #         print 'SUCCESS'
                #     else:
                #         print 'TIMEOUT'


                pos = fp.tell()

                fp.close()
                self.t.close()
        except:
            self.t.close()
            return -1

    ############################################################################

################################################################################

def main():

    cli = ChimeraWatcher()
    cli.run()

################################################################################

if __name__ == '__main__':
    main()

################################################################################
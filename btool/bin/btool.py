import splunk.Intersplunk as si
import sys

if __name__ == '__main__':

    conf=''
    stanza_asked=''
    try:
        if len(sys.argv) > 2:
            conf = sys.argv[2]
        else:
            raise Exception("Usage: btool confName [stanza]")

        if len(sys.argv) > 3:
            stanza_asked = sys.argv[3]

        (isgetinfo, sys.argv) = si.isGetInfo(sys.argv)

        if isgetinfo:
            reqsop = True
            preop = "prebtool " + conf + " " + stanza_asked
            si.outputInfo(False, False, False, reqsop, preop) # calls sys.exit()

        results = si.readResults(None, None, False)
        si.outputResults(results)

    except Exception, e:
        si.generateErrorResults(e)

__author__ = 'Edward'


class McnpSurfTree:
    pass


class McnpMacrobody:
    pass


class McnpReadState:
    """
    Holds the current state of file reading
    """

    CELL = 1
    SURF = 2
    DATA = 3
    AUX = 4

    def __init__(self):
        self.lineno = 1
        self.cardno = 1
        self.deck = McnpReadState.CELL
        self.title = False
        self.comment = False
        self.errors = []


class McnpFileLine:
    """
    Represents a single actual line of a MCNP card
    """

    def __init__(self, linedata, readstate):
        self.raw = linedata
        self.rawlength = len(self.raw)
        self.comment = ""
        self.length = -1
        self.cmdtoken = ""
        self.data = ""
        self.lineno = readstate.lineno

        # Strip the comment
        data = self.raw
        try:
            data, self.comment = self.raw.split('$', 1)
            #print("fetched comment")
        except ValueError:
            pass  # no comment - do nothing
        #print("after data = " + data)

        # Throw away extra whitespace
        data = data.rstrip()
        self.length = len(data)

        # Check the data segment for formatting
        if '\t' in data:
            print("WARNING: line " + str(readstate.lineno) + " contains tabs")
            readstate.errors.append((readstate.lineno, McnpError.CONTAINS_TABS))
        if data.startswith(' '):
            print("WARNING: line " + str(readstate.lineno) + " starts with whitespace")
            readstate.errors.append((readstate.lineno, McnpError.LEADING_WHITE))
        if self.length > 80:
            print("ERROR: line " + str(readstate.lineno) + " exceeds 80 characters")
            readstate.errors.append((readstate.lineno, McnpError.OVER_80_CHAR))

        # Strip the command token from the data
        self.cmdtoken = ""
        #print("prior, data = " + data)
        try:
            #print("data = " + data)
            self.cmdtoken, data = data.split(' ', 1)
        except ValueError:
            # Comments need nothing more than a command token
            if not readstate.comment:
                print("ERROR: No command token found @ line " + str(readstate.lineno))
                readstate.errors.append((readstate.lineno, McnpError.NO_CMD_TOKEN))
            else:
                self.cmdtoken = "c"
                data = ""
        #print("pose data = " + data)

        if len(self.cmdtoken) > 5 and not readstate.title:
            pass

        self.data = data.strip()
        #print("final data = " + self.data)

    def __str__(self):
        return self.raw


class McnpError:
    """
    Has a whole bunch of warning/error codes
    """

    CONTAINS_TABS = 1
    LEADING_WHITE = 2
    OVER_80_CHAR = 3

    PAREN_MISMATCH = 4

    INCOMPLETE_CARD = 9

    GEO_ERROR = 10
    DOUBLE_CELL_ID = 11
    DOUBLE_SURF_ID = 12
    DOUBLE_MAT_ID = 13
    DOUBLE_F_ID = 14
    UNREF_DISTRIB = 15

    NO_SUCH_MAT = 20
    NO_SUCH_CELL = 21
    NO_SUCH_SURF = 22

    NOT_ENOUGH_ENTRY = 30
    TOO_MANY_ENTRY = 31

    NO_CMD_TOKEN = 40
    BAD_CMD_TOKEN = 41

    def __init__(self):
        self.errors = []

    def fail(self):
        return len(self.errors) == 0

    def code_string(self, code):
        if code == McnpError.CONTAINS_TABS:
            return "Contains Tabs"
        elif code == McnpError.OVER_80_CHAR:
            return "Over 80 characters in length"
        elif code == McnpError.PAREN_MISMATCH:
            return "Parenthesis Mismatch"
        else:
            return "Unknown error code (" + str(code) + ")"
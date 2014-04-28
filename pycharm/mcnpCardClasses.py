__author__ = 'Edward'

import mcnpCardInternals
import queue
import re


class McnpInputFile:
    """
    Represents an entire MCNP input data file
    """

    def __init__(self, filename=""):
        self.celldeck = McnpCellDeck()
        self.surfdeck = McnpSurfDeck()
        self.datadeck = McnpDataDeck()
        self.auxdeck = McnpAuxDeck()
        self.filename = filename
        self.file = None
        self.rawdata = []
        self.queuedata = queue.Queue()
        self.readstate = mcnpCardInternals.McnpReadState()

    def setfilename(self, filename):
        self.filename = filename

    def parse(self):
        # Read the file
        try:
            self.file = open(self.filename)
        except IOError:
            print("Could not read file: " + self.filename)
            return False

        # Put the data in the rew data queue
        for line in self.file.readlines():
            self.rawdata.append(line)
            self.queuedata.put(line)

        # Parse the file
        if not self.celldeck.parse(self.queuedata, self.readstate):
            print("Failed to parse Cell Deck")

        if not self.surfdeck.parse(self.queuedata, self.readstate):
            print("Failed to parse Surf Deck")

        if not self.datadeck.parse(self.queuedata, self.readstate):
            print("Failed to parse Data Deck")

        if not self.auxdeck.parse(self.queuedata, self.readstate):
            print("Failed to parse Aux Deck")


class McnpCellDeck:
    """
    Represents the cell deck of an MCNP input file up to the first blank line
    """

    def __init__(self):
        self.cards = []

    def parse(self, dataqueue, readstate):

        # Read the title
        newcard = McnpTitleCard()
        #print("cell deck is parsing title card")
        newcard.parse(dataqueue.get(block=True, timeout=1), dataqueue, readstate)
        self.cards.append(newcard)
        #print(str(newcard))

        # Read the next line
        line = dataqueue.get(block=True, timeout=1)

        while line.strip() != "":
            cmdtoken = line.lstrip().split(' ', 1)[0]

            # Determine the card type
            if cmdtoken == "c" or cmdtoken == "C":
                #print("comment")
                newcard = McnpCommentCard()
            elif re.match('^\d{1,5}$', cmdtoken):
                #print("cell")
                newcard = McnpCellCard()
            else:
                #print("??? BAD ???")
                newcard = McnpBadCard()

            # Parse the card and add it to the list
            newcard.parse(line, dataqueue, readstate)
            #print("after McnpCellDeck:: ~~~.parse(): cardata = " + newcard.carddata)
            self.cards.append(newcard)

            #print("after pars")
            #print(str(newcard))

            # Advance to next card
            line = dataqueue.get(block=True, timeout=1)

        return True

    def __str__(self):
        r = ""
        for card in self.cards:
            r += str(card) + "\n"
        return r


class McnpSurfDeck:
    """
    Represents the surface definitions from a MCNP file
    """

    def __init__(self):
        self.cards = None

    def parse(self, dataqueue, readstate):
        pass


class McnpDataDeck:
    """
    Represents all data cards in an MCNP input file
    """

    def __init__(self):
        self.cards = None

    def parse(self, dataqueue, readstate):
        pass


class McnpAuxDeck:
    """
    Represents all the comments after the data deck
    """

    def __init__(self):
        self.cards = None

    def parse(self, dataqueue, readstate):
        pass


class McnpCard:
    """
    Represents a single card (may be multi-line)
    """

    def __init__(self):
        self.lines = []
        self.cardno = -1
        self.cmdtoken = ""
        self.carddata = ""

    def parse(self, dataline, dataqueue, readstate):
        print("McnpCard::parse() not implemented")


class McnpCommentCard(McnpCard):
    """
    Comment card that begins with 'c '
    """

    def __init__(self):
        super(McnpCommentCard, self).__init__()
        self.comment = ""

    def parse(self, dataline, dataqueue, readstate):
        readstate.comment = True
        self.lines.append(mcnpCardInternals.McnpFileLine(dataline, readstate))
        readstate.comment = False

        #print("raw data = " + str(self.lines[-1].data))
        self.carddata += self.lines[-1].data
        #print("carddata = " + self.carddata)

        self.cardno = readstate.cardno
        readstate.lineno += 1
        readstate.cardno += 1

    def __str__(self):
        #print("in __str__ cardata = " + self.carddata)
        #return str(self.cardno) + " #> " + self.carddata
        return str("{0: >2}".format(self.cardno) + " #       > " + self.carddata)


class McnpCellCard(McnpCard):
    """
    Mcnp cell card
    """

    def __init__(self):
        super(McnpCellCard, self).__init__()
        self.id = -1

    def parse(self, dataline, dataqueue, readstate):
        self.lines.append(mcnpCardInternals.McnpFileLine(dataline, readstate))

        # Copy data
        self.cmdtoken = self.lines[-1].cmdtoken
        self.carddata += self.lines[-1].data
        self.cardno = readstate.cardno

        # Get additional lines of data
        while self.carddata.endswith("&"):
            self.carddata = self.carddata[:-1]  # Throw away '&'
            self.lines.append(mcnpCardInternals.McnpFileLine(dataqueue.get(block=True, timeout=1), readstate))
            self.carddata += self.lines[-1].data
            readstate.lineno += 1

        # Validate data
        try:
            self.id = int(self.cmdtoken)
        except ValueError:
            print("ERROR: Could not transform cmd token on line " + str(readstate.lineno) +
                  " to integer ('" + self.cmdtoken + "')")
            readstate.errors.append((readstate.lineno, mcnpCardInternals.McnpError.BAD_CMD_TOKEN))

        # Prep the readstate for the next card
        readstate.lineno += 1
        readstate.cardno += 1

    def __str__(self):
        return str("{0: >2}".format(self.cardno) + " C " + "{0: >5}".format(self.id) + " > " + self.carddata)


class McnpTitleCard(McnpCard):
    """
    Title card - The first line of the file
    """

    def __init__(self):
        super(McnpTitleCard, self).__init__()
        self.title = ""

    def parse(self, dataline, dataqueue, readstate):
        readstate.title = True
        self.lines.append(mcnpCardInternals.McnpFileLine(dataline, readstate))
        readstate.title = False

        self.cardno = readstate.cardno
        self.carddata = self.lines[-1].raw.rstrip()
        self.title = self.carddata

        # Prep the readstate for the next card
        readstate.lineno += 1
        readstate.cardno += 1

    def __str__(self):
        return str("{0: >2}".format(self.cardno) + " T       > " + self.title)


class McnpSurfCard(McnpCard):
    """
    Mcnp surface card
    """

    def __init__(self):
        super(McnpSurfCard, self).__init__()
        self.surf = ""
        self.args = []


class McnpDataCard(McnpCard):
    """
    Mcnp Data Card
    """

    def __init__(self):
        super(McnpDataCard, self).__init__()
        self.surf = ""
        self.args = []


class McnpBadCard(McnpCard):
    """
    Erroneous card - could not be read
    """

    def __init__(self):
        super(McnpBadCard, self).__init__()
        self.surf = ""
        self.args = []
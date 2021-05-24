class StarBattleCommand:
    def __init__(self, stars=None, noStars=None, doubles=None, triples=None):
        self._stars = stars
        self._noStars = noStars
        self._doubles = doubles
        self._triples = triples

        if self._stars is None:
            self._stars = []
        if self._noStars is None:
            self._noStars = []
        if self._doubles is None:
            self._doubles = []
        if self._triples is None:
            self._triples = []

        self._type = None

    def __str__(self):
        return "[{0}] stars: {1} | noStars: {2} " \
               "| doubles: {3} | triples: {4}".format(self._type, self._stars, self._noStars,
                                                      self._doubles, self._triples)

    def GetStars(self):
        return self._stars

    def GetNoStars(self):
        return self._noStars

    def GetDoubles(self):
        return self._doubles

    def GetTriples(self):
        return self._triples

    def SetType(self, t):
        self._type = t


class StarBattleCommandPuzzleBreak(StarBattleCommand):
    def __init__(self, noStars, subCommands):
        super(StarBattleCommandPuzzleBreak, self).__init__(noStars=noStars)
        self._subCommands = subCommands

    def __str__(self):
        s = "[B] noStars: {0} because of puzzle break:\n".format(self._noStars)

        i = 0
        for c in self._subCommands:
            s += "({0})--- {1}\n".format(i, str(c))
            i += 1
        return s

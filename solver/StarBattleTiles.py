from solver.StarBattleEnums import StarBattleTileStates


class StarBattleTile:
    def __init__(self):
        self._status = StarBattleTileStates.UNKNOWN

    def Status(self):
        return self._status

    def SetStatus(self, status):
        self._status = status

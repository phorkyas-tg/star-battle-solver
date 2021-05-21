from enum import Enum


class StarBattleSolverError(Exception):
    pass


class StarBattleGridCodes(Enum):
    OK = 0
    # cell count is not dim * dim
    INVALID_CELL_COUNT = 1
    # a position is not inside the grid
    INVALID_DIMENSION = 2
    # the number of areas is not equal to the dim
    INVALID_AREA_COUNT = 3
    # the number of tiles aren't possible
    INVALID_AREA_SIZE = 4
    # there is at least one duplication in the positions
    DUPLICATE_POSITION = 5
    # a tile of one area is disconnected from the rest
    DISCONNECTED_TILE = 6

    # the grid is not solvable
    UNSOLVABLE = 99


class StarBattleTileStates(Enum):
    UNKNOWN = 0
    NO_STAR = 1
    STAR = 2
    TWIN = 3


class StarBattleCommand:
    def __init__(self, stars, noStars):
        self._stars = stars
        self._noStars = noStars

    def __str__(self):
        return "stars: {0} | noStars {1}".format(self._stars, self._noStars)

    def GetStars(self):
        return self._stars

    def GetNoStars(self):
        return self._noStars


class StarBattleTile:
    def __init__(self):
        self._status = StarBattleTileStates.UNKNOWN

    def Status(self):
        return self._status

    def SetStatus(self, status):
        self._status = status


class StarBattleSolver:

    @staticmethod
    def IsValidStarBattleGrid(battleSolverGrid: dict, dimension: int = 9, stars: int = 2):
        if sum([len(c) for c in battleSolverGrid.values()]) != dimension * dimension:
            return StarBattleGridCodes.INVALID_CELL_COUNT

        if len(list(battleSolverGrid.keys())) != dimension:
            return StarBattleGridCodes.INVALID_AREA_COUNT

        knownPositions = []

        minimalAreaSize = 2 * stars - 1
        for key, posList in battleSolverGrid.items():

            if len(posList) < minimalAreaSize:
                return StarBattleGridCodes.INVALID_AREA_SIZE

            for pos in posList:
                if pos in knownPositions:
                    return StarBattleGridCodes.DUPLICATE_POSITION
                knownPositions.append(pos)

                if not StarBattleSolver.IsInGrid(pos):
                    return StarBattleGridCodes.INVALID_DIMENSION

                for otherPos in posList:
                    if pos != otherPos and StarBattleSolver.IsAdjacent(pos, otherPos, False):
                        break
                else:
                    return StarBattleGridCodes.DISCONNECTED_TILE

        return StarBattleGridCodes.OK

    @staticmethod
    def IsInGrid(pos: tuple, dimension: int = 9):
        return (0 <= pos[0] <= dimension - 1) and (0 <= pos[1] <= dimension - 1)

    @staticmethod
    def IsAdjacent(pos1: tuple, pos2: tuple, checkDiagonal: bool = False):
        deltaX = abs(pos1[0] - pos2[0])
        deltaY = abs(pos1[1] - pos2[1])

        if deltaX > 1 or deltaY > 1 or (deltaX == 0 and deltaY == 0):
            return False

        if checkDiagonal:
            return True

        if (deltaX == 0 and deltaY == 1) or (deltaX == 1 and deltaY == 0):
            return True

        return False

    def __init__(self, boardData, dimension, stars=2, validateData=True):
        returnCode = StarBattleSolver.IsValidStarBattleGrid(boardData, dimension, stars)
        if validateData and returnCode != StarBattleGridCodes.OK:
            raise StarBattleSolverError("Invalid BattleSolver grid: {0}".format(returnCode.name))

        self._dimension = dimension
        self._stars = stars
        self._boardData = boardData
        self._board = []
        self._commands = []

        for r in range(self._dimension):
            row = []
            for c in range(self._dimension):
                row.append(StarBattleTile())
            self._board.append(row)

    def GetAdjacentPositions(self, pos: tuple):
        adjacentPositions = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                if x == 0 and y == 0:
                    continue
                newPos = (pos[0] + x, pos[1] + y)
                if self.IsInGrid(newPos, self._dimension):
                    adjacentPositions.append(newPos)
        return adjacentPositions

    def Commit(self, command: StarBattleCommand):
        self._commands.append(command)
        for star in command.GetStars():
            self._board[star[0]][star[1]].SetStatus(StarBattleTileStates.STAR)
        for noStar in command.GetNoStars():
            self._board[noStar[0]][noStar[1]].SetStatus(StarBattleTileStates.NO_STAR)

    def NextSolution(self):
        # Check all Rows
        for r in range(self._dimension):
            row = self.GetRow(r, [StarBattleTileStates.UNKNOWN, StarBattleTileStates.STAR,
                                  StarBattleTileStates.TWIN])
            solutions = self.GetPossibleSolutions(row)
            command = self.InterpretSolutions(solutions)
            if command:
                return command

        # Check all Columns
        for c in range(self._dimension):
            column = self.GetColumn(c, [StarBattleTileStates.UNKNOWN, StarBattleTileStates.STAR,
                                        StarBattleTileStates.TWIN])
            solutions = self.GetPossibleSolutions(column)
            command = self.InterpretSolutions(solutions)
            if command:
                return command

        # Check all areas
        for key in self._boardData.keys():
            area = self.GetArea(key, [StarBattleTileStates.UNKNOWN, StarBattleTileStates.STAR,
                                      StarBattleTileStates.TWIN])
            solutions = self.GetPossibleSolutions(area)
            command = self.InterpretSolutions(solutions)
            if command:
                return command

    def GetRow(self, r, flt):
        return [(r, i) for i, tile in enumerate(self._board[r]) if tile.Status() in flt]

    def GetColumn(self, c, flt):
        column = []
        for r in range(self._dimension):
            if self._board[r][c].Status() in flt:
                column.append((r, c))
        return column

    def GetArea(self, key, flt):
        area = []
        for pos in self._boardData[key]:
            if self._board[pos[0]][pos[1]].Status() in flt:
                area.append((pos[0], pos[1]))
        return area

    def InterpretSolutions(self, solutions):
        if len(solutions) == 1:
            return StarBattleCommand(solutions[0]["stars"], solutions[0]["noStars"])
        return None

    def GetPossibleSolutions(self, positions):
        stars = []
        filteredPositions = []
        for pos in positions:
            if self._board[pos[0]][pos[1]].Status() == StarBattleTileStates.STAR:
                stars.append(pos)
            else:
                filteredPositions.append(pos)

        if len(stars) == self._stars:
            if filteredPositions:
                stars.sort()
                filteredPositions.sort()
                return [{"stars": stars, "noStars": filteredPositions}]
            return []

        return self._GetPossibleSoltionsRecursive(filteredPositions, stars)

    def _GetPossibleSoltionsRecursive(self, filteredPositions, stars, noStars=None, solutions=None):
        if noStars is None:
            noStars = []
        if solutions is None:
            solutions = []

        # Set next star for all filtered solutions
        for pos in filteredPositions:
            newStars = stars.copy()
            newStars.append(pos)
            newStars.sort()

            # if this combination is already in the results list skip it
            if newStars in [r["stars"] for r in solutions]:
                continue

            # get all the known noStars and add the new ones from the new star
            newNoStars = noStars.copy()
            for noStar in self.GetAdjacentPositions(pos):
                if noStar not in newNoStars:
                    newNoStars.append(noStar)

            newFilteredPositions = [p for p in filteredPositions
                                    if p not in newStars and p not in newNoStars]

            # termination new stars equal to the max star count
            if len(newStars) == self._stars:
                # add the rest of all positions because they must be noStars
                newNoStars.extend(newFilteredPositions)
                newNoStars.sort()
                # add this solution to the solutions
                solutions.append({"stars": newStars, "noStars": newNoStars})
                continue

            self._GetPossibleSoltionsRecursive(newFilteredPositions, newStars, newNoStars,
                                               solutions)

        return solutions


from enum import Enum
import copy


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

        self._doubles = []
        self._triples = []

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

    def GetStatus(self):
        solved = True
        broken = False

        for d in range(self._dimension):
            rowStars = len(self.GetRow(d, [StarBattleTileStates.STAR]))
            columnStars = len(self.GetRow(d, [StarBattleTileStates.STAR]))
            rowNoStars = len(self.GetRow(d, [StarBattleTileStates.NO_STAR]))
            columnNoStars = len(self.GetRow(d, [StarBattleTileStates.NO_STAR]))

            if rowStars != self._stars or columnStars != self._stars:
                solved = False

            if rowStars > self._stars or columnStars > self._stars:
                broken = True

            if rowNoStars >= self._dimension or columnNoStars >= self._dimension:
                broken = True

        for key, positions in self._boardData.items():
            areaStars = len(self.GetArea(key, [StarBattleTileStates.STAR]))
            areaNoStars = len(self.GetArea(key, [StarBattleTileStates.NO_STAR]))

            if areaStars != self._stars or areaStars != self._stars:
                solved = False

            if areaStars > self._stars or areaStars > self._stars:
                broken = True

            if areaNoStars >= len(positions) or areaNoStars >= len(positions):
                broken = True

        return solved, broken

    def Commit(self, command: StarBattleCommand, silent=False):
        if not silent:
            self._commands.append(command)

        newPositions = []
        for star in command.GetStars():
            self._board[star[0]][star[1]].SetStatus(StarBattleTileStates.STAR)
            newPositions.append(star)
        for noStar in command.GetNoStars():
            self._board[noStar[0]][noStar[1]].SetStatus(StarBattleTileStates.NO_STAR)
            newPositions.append(noStar)

        unnecessaryDoubles = []
        for newPosition in newPositions:
            for double in self._doubles:
                if newPosition in double and double not in unnecessaryDoubles:
                    unnecessaryDoubles.append(double)
        for ud in unnecessaryDoubles:
            self._doubles.remove(ud)

        unnecessaryTriples = []
        for newPosition in newPositions:
            for triple in self._triples:
                if newPosition in triple and triple not in unnecessaryTriples:
                    unnecessaryTriples.append(triple)
        for ut in unnecessaryTriples:
            self._triples.remove(ut)

    def GetSingleDimensionCommand(self, getter, d, commandType):
        positions = getter(d, [StarBattleTileStates.UNKNOWN, StarBattleTileStates.STAR])
        solutions = self.GetPossibleSolutions(positions)
        command = self.InterpretSolutions(solutions)
        if command:
            command.SetType("{0}{1}".format(commandType, d))
            return command
        return None

    def GetMultiDimensionCommand(self, getter, commandType):
        for d1 in range(self._dimension):
            dimSum = []
            dimCount = 0
            for d2 in range(d1, self._dimension):
                dimSum.extend(getter(d2, [StarBattleTileStates.UNKNOWN,
                                          StarBattleTileStates.STAR]))
                dimCount += 1
                areaCount = 0
                dimSumTemp = dimSum.copy()
                for key in self._boardData:
                    area = self.GetArea(key, [StarBattleTileStates.UNKNOWN,
                                              StarBattleTileStates.STAR])
                    for pos in area:
                        if pos not in dimSum:
                            break
                    else:
                        areaCount += 1
                        for pos in area:
                            dimSumTemp.remove(pos)

                if dimCount == areaCount and len(dimSumTemp) > 0:
                    command = StarBattleCommand(noStars=dimSumTemp)
                    command.SetType("{0}M{1}-{2}".format(commandType, d1, d2))
                    return command
        return None

    def NextSolution(self, tryPuzzleBreak=True):
        # Check all single rows
        for d in range(self._dimension):
            command = self.GetSingleDimensionCommand(self.GetRow, d, "R")
            if command:
                return command

        # Check all single columns
        for d in range(self._dimension):
            command = self.GetSingleDimensionCommand(self.GetColumn, d, "C")
            if command:
                return command

        # Check all single areas
        for key in self._boardData.keys():
            command = self.GetSingleDimensionCommand(self.GetArea, key, "A")
            if command:
                return command

        # Check multiple rows
        command = self.GetMultiDimensionCommand(self.GetRow, "R")
        if command:
            return command

        # Check multiple columns
        command = self.GetMultiDimensionCommand(self.GetColumn, "C")
        if command:
            return command

        # As a last resort try a field and look if something breaks
        if tryPuzzleBreak:
            unknownPositions = []
            for r in range(self._dimension):
                for c in range(self._dimension):
                    if self._board[r][c].Status() == StarBattleTileStates.UNKNOWN:
                        unknownPositions.append((r, c))

            for depth in range(30):
                command = self.TryPuzzleBreak(unknownPositions, depth)
                if command:
                    return command

    def TryPuzzleBreak(self, unknownPositions, depth):
        boardTemp, doublesTemp, triplesTemp = self.CopyBoard(self._board, self._doubles,
                                                             self._triples)
        breakCommand = None
        for pos in unknownPositions:
            # reset board
            self._board, self._doubles, self._triples = self.CopyBoard(boardTemp, doublesTemp,
                                                                       triplesTemp)
            isBroken = False
            newStar = [pos]
            newNoStars = []
            for noStar in self.GetAdjacentPositions(pos):
                if self._board[noStar[0]][noStar[1]].Status() != StarBattleTileStates.NO_STAR:
                    newNoStars.append(noStar)

            command = StarBattleCommand(stars=newStar, noStars=newNoStars)
            self.Commit(command, silent=True)

            subCommands = []
            for i in range(depth):
                command = self.NextSolution(tryPuzzleBreak=False)
                subCommands.append(command)
                if command is None:
                    break
                self.Commit(command, silent=True)
                solved, broken = self.GetStatus()

                if solved:
                    break
                if broken:
                    isBroken = True
                    break

            if isBroken:
                breakCommand = StarBattleCommandPuzzleBreak([pos], subCommands)
                break

        # reset board
        self._board, self._doubles, self._triples = self.CopyBoard(boardTemp, doublesTemp,
                                                                   triplesTemp)
        return breakCommand

    def CopyBoard(self, board, doubles, triples):
        newBoard = []
        newDoubles = copy.deepcopy(doubles)
        newTriples = copy.deepcopy(triples)

        for r in range(self._dimension):
            row = []
            for c in range(self._dimension):
                row.append(StarBattleTile())
            newBoard.append(row)

        for r in range(self._dimension):
            for c in range(self._dimension):
                if board[r][c].Status() == StarBattleTileStates.UNKNOWN:
                    newBoard[r][c].SetStatus(StarBattleTileStates.UNKNOWN)
                if board[r][c].Status() == StarBattleTileStates.STAR:
                    newBoard[r][c].SetStatus(StarBattleTileStates.STAR)
                if board[r][c].Status() == StarBattleTileStates.NO_STAR:
                    newBoard[r][c].SetStatus(StarBattleTileStates.NO_STAR)

        return newBoard, newDoubles, newTriples

    def GetRow(self, r: int, flt: list):
        return [(r, i) for i, tile in enumerate(self._board[r]) if tile.Status() in flt]

    def GetColumn(self, c: int, flt: list):
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
        if len(solutions) == 0:
            return None

        if len(solutions) == 1:
            return StarBattleCommand(stars=solutions[0]["stars"], noStars=solutions[0]["noStars"])

        forcedStars = self.GetForcedSolutions(solutions, "stars", StarBattleTileStates.STAR)
        forcedNoStars = self.GetForcedSolutions(solutions, "noStars", StarBattleTileStates.NO_STAR)

        if len(forcedStars) > 0 or len(forcedNoStars) > 0:
            return StarBattleCommand(stars=forcedStars, noStars=forcedNoStars)

        if self.GetDoubles(solutions, "stars", StarBattleTileStates.STAR):
            return StarBattleCommand(doubles=self._doubles)

        if self.GetTriples(solutions, "stars", StarBattleTileStates.STAR):
            return StarBattleCommand(triples=self._triples)

        return None

    def GetDoubles(self, solutions, key, flt):
        countPositions = {}
        filteredSolutions = [s[key] for s in solutions]
        for solution in filteredSolutions:
            for pos in solution:
                if self._board[pos[0]][pos[1]].Status() != flt:
                    countPositions.setdefault(pos, 0)
                    countPositions[pos] += 1

        doublesChanged = False
        for firstPos, firstValue in countPositions.items():
            for secondPos, secondValue in countPositions.items():
                if firstPos == secondPos:
                    continue
                if firstValue + secondValue == len(solutions) and \
                        self.IsAdjacent(firstPos, secondPos, False):

                    newDouble = [firstPos, secondPos]
                    newDouble.sort()
                    if newDouble not in self._doubles:
                        self._doubles.append(newDouble)
                        doublesChanged = True

        return doublesChanged

    def GetTriples(self, solutions, key, flt):
        countPositions = {}
        filteredSolutions = [s[key] for s in solutions]
        for solution in filteredSolutions:
            for pos in solution:
                if self._board[pos[0]][pos[1]].Status() != flt:
                    countPositions.setdefault(pos, 0)
                    countPositions[pos] += 1

        triplesChanged = False
        for firstPos, firstValue in countPositions.items():
            for secondPos, secondValue in countPositions.items():
                for thirdPos, thirdValue in countPositions.items():
                    if firstPos == secondPos or firstPos == thirdPos or secondPos == thirdPos:
                        continue

                    validTriple = True
                    for solution in filteredSolutions:
                        if firstPos not in solution and secondPos not in solution and \
                                thirdPos not in solution:
                            validTriple = False
                    if validTriple:

                        if not self.IsAdjacent(firstPos, secondPos, False) and \
                                not self.IsAdjacent(firstPos, thirdPos, False):
                            continue
                        if not self.IsAdjacent(secondPos, firstPos, False) and \
                                not self.IsAdjacent(secondPos, thirdPos, False):
                            continue
                        if not self.IsAdjacent(thirdPos, firstPos, False) and \
                                not self.IsAdjacent(thirdPos, secondPos, False):
                            continue

                        if not firstPos[0] == secondPos[0] == thirdPos[0] and \
                                not firstPos[1] == secondPos[1] == thirdPos[1]:
                            continue

                        newTriple = [firstPos, secondPos, thirdPos]
                        newTriple.sort()
                        if newTriple not in self._triples:
                            self._triples.append(newTriple)
                            triplesChanged = True

        return triplesChanged

    def GetForcedSolutions(self, solutions, key, flt):
        foundForced = []
        filteredSolutions = [s[key] for s in solutions]
        for pos in filteredSolutions[0]:
            if self._board[pos[0]][pos[1]].Status() != flt:
                for otherSolution in filteredSolutions[1:]:
                    if pos not in otherSolution:
                        break
                else:
                    foundForced.append(pos)
        return foundForced

    def GetNoStarsFromForcedSolutions(self, forcedSolutions, noStarPositions, starCount):
        filteredForcedSolutions = []
        for forcedSolution in forcedSolutions:
            for pos in forcedSolution:
                if pos not in noStarPositions:
                    break
            else:
                filteredForcedSolutions.append(forcedSolution.copy())

        newFilteredPositions = []
        if len(filteredForcedSolutions) + starCount == self._stars:
            for pos in noStarPositions:
                for forcedSolution in filteredForcedSolutions:
                    if pos in forcedSolution:
                        break
                else:
                    newFilteredPositions.append(pos)
        return newFilteredPositions

    def GetPossibleSolutions(self, positions):
        stars = []
        filteredPositions = []
        for pos in positions:
            if self._board[pos[0]][pos[1]].Status() == StarBattleTileStates.STAR:
                stars.append(pos)
            else:
                filteredPositions.append(pos)

        # Check if there are already N stars
        if len(stars) == self._stars:
            # if there are Unknown positions then all these positions must be noStars
            if filteredPositions:
                stars.sort()
                filteredPositions.sort()
                return [{"stars": [], "noStars": filteredPositions}]
            return []

        # Check doubles
        newFilteredPositions = self.GetNoStarsFromForcedSolutions(self._doubles,
                                                                  filteredPositions, len(stars))
        if newFilteredPositions:
            return [{"stars": [], "noStars": newFilteredPositions}]

        # # Check triples
        newFilteredPositions = self.GetNoStarsFromForcedSolutions(self._triples,
                                                                  filteredPositions, len(stars))
        if newFilteredPositions:
            return [{"stars": [], "noStars": newFilteredPositions}]

        return self._GetPossibleSolutionsRecursive(filteredPositions, stars)

    def _GetPossibleSolutionsRecursive(self, filteredPositions, stars, noStars=None,
                                       solutions=None):
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
                if noStar not in newNoStars and \
                        self._board[noStar[0]][noStar[1]].Status() != StarBattleTileStates.NO_STAR:
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

            self._GetPossibleSolutionsRecursive(newFilteredPositions, newStars, newNoStars,
                                                solutions)

        return solutions


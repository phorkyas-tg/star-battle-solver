import copy

from solver.StarBattleCommands import StarBattleCommand, StarBattleCommandPuzzleBreak
from solver.StarBattleTiles import StarBattleTile
from solver.StarBattleEnums import StarBattleGridCodes, StarBattleTileStates


class StarBattleSolverError(Exception):
    pass


class StarBattleSolver:

    @staticmethod
    def IsValidStarBattleGrid(battleSolverGrid, dimension=9, stars=2):
        """
        Checks if the given grid is a valid star battle grid. It checks the cell count,
        dimensions, area count, area size, duplicates or disconnected tiles. It does not check if
        the grid is actually solvable. As a result the function returns a code.

        :param battleSolverGrid: areas (key) with their tile positions list(tuple(int, int))
        :type battleSolverGrid: dict
        :param dimension: dimension of the grid
        :type dimension: int
        :param stars: number of stars per row/columns/area
        :type stars: int
        :return: grid code
        :rtype: StarBattleGridCodes
        """
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
    def IsInGrid(pos, dimension=9):
        """
        Checks if the given position is in the grid

        :param pos: position
        :type pos: tuple(int, int)
        :param dimension: dimension of the grid
        :type dimension: int
        :return: True if position is in grid else False
        :rtype: bool
        """
        return (0 <= pos[0] <= dimension - 1) and (0 <= pos[1] <= dimension - 1)

    @staticmethod
    def IsAdjacent(pos1, pos2, checkDiagonal=False):
        """
        Checks if the two given positions are adjaced to one another

        :param pos1: first position
        :type pos1: tuple(int, int)
        :param pos2: second position
        :type pos2: tuple(int, int)
        :param checkDiagonal: If True also check the diagonal position
        :type checkDiagonal: bool
        :return:
        :rtype: bool
        """
        deltaX = abs(pos1[0] - pos2[0])
        deltaY = abs(pos1[1] - pos2[1])

        if deltaX > 1 or deltaY > 1 or (deltaX == 0 and deltaY == 0):
            return False

        if checkDiagonal:
            return True

        if (deltaX == 0 and deltaY == 1) or (deltaX == 1 and deltaY == 0):
            return True

        return False

    @staticmethod
    def GetAdjacentPositions(pos, dimension):
        """
        Get a list of all 9 adjacent positions of the given postion. Remove any positions that are
        not in the grid.

        :param pos: position
        :type pos: tuple(int, int)
        :param dimension: dimension of the grid
        :type dimension: int
        :return: list of adjacent positions
        :rtype: list(tuple(int, int))
        """
        adjacentPositions = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                if x == 0 and y == 0:
                    continue
                newPos = (pos[0] + x, pos[1] + y)
                if StarBattleSolver.IsInGrid(newPos, dimension):
                    adjacentPositions.append(newPos)
        return adjacentPositions

    @staticmethod
    def CopyBoard(board, doubles, triples, dimension):
        """
        Make a deep copy of the board, doubles and triples.

        :param board: board matrix
        :type board: list(list(StarBattleTile))
        :param doubles: list of double
        :type doubles: list(list(tuple(int, int)))
        :param triples: list of triples
        :type triples: list(list(tuple(int, int)))
        :param dimension: dimension of the grid
        :type dimension: int
        :return:
        :rtype: list(list(StarBattleTile)), list(list(tuple(int, int))), list(list(tuple(int, int)))
        """

        newBoard = []
        newDoubles = copy.deepcopy(doubles)
        newTriples = copy.deepcopy(triples)

        for r in range(dimension):
            row = []
            for c in range(dimension):
                row.append(StarBattleTile())
            newBoard.append(row)

        for r in range(dimension):
            for c in range(dimension):
                if board[r][c].Status() == StarBattleTileStates.UNKNOWN:
                    newBoard[r][c].SetStatus(StarBattleTileStates.UNKNOWN)
                if board[r][c].Status() == StarBattleTileStates.STAR:
                    newBoard[r][c].SetStatus(StarBattleTileStates.STAR)
                if board[r][c].Status() == StarBattleTileStates.NO_STAR:
                    newBoard[r][c].SetStatus(StarBattleTileStates.NO_STAR)

        return newBoard, newDoubles, newTriples

    def __init__(self, boardData, dimension=9, stars=2, validateData=True):
        """
        Init the solver

        :param boardData: areas (key) with their tile positions list(tuple(int, int))
        :type boardData: dict
        :param dimension: dimension of the grid
        :type dimension: int
        :param stars: number of stars per row/columns/area
        :type stars: int
        :param validateData: If True validate grid and raise an StarBattleSolverError if there
        is a problem
        :type validateData: bool
        """
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

    def GetStatus(self):
        """
        Get the current status of the board. The first return value tells if the board is already
        solved. The other if it is broken.

        :return: solved, broken
        :rtype: bool, bool
        """
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

    def GetRow(self, r, flt):
        """
        Get specific row from board

        :param r: index
        :type r: int
        :param flt: tile filter
        :type flt: list(StarBattleTileStates)
        :return: list of positions
        :rtype: list(tuple(int, int))
        """
        return [(r, i) for i, tile in enumerate(self._board[r]) if tile.Status() in flt]

    def GetColumn(self, c, flt):
        """
        Get specific colum from board

        :param c: index
        :type c: int
        :param flt: tile filter
        :type flt: list(StarBattleTileStates)
        :return: list of positions
        :rtype: list(tuple(int, int))
        """
        column = []
        for r in range(self._dimension):
            if self._board[r][c].Status() in flt:
                column.append((r, c))
        return column

    def GetArea(self, key, flt):
        """
        Get specific area from board

        :param key: key
        :type key: str
        :param flt: tile filter
        :type flt: list(StarBattleTileStates)
        :return: list of positions
        :rtype: list(tuple(int, int))
        """
        area = []
        for pos in self._boardData[key]:
            if self._board[pos[0]][pos[1]].Status() in flt:
                area.append((pos[0], pos[1]))
        return area

    def Commit(self, command, silent=False):
        """
        Setting the board to the tile states of all given positions. Get rid of broken doubles and
        triples. Add the command to the command list.

        :param command: Command with all positions and tile states
        :type command: StarBattleCommand
        :param silent: If True the command does not appear in the command list
        :type silent: bool
        """
        if not silent:
            self._commands.append(command)

        newPositions = []
        for star in command.GetStars():
            self._board[star[0]][star[1]].SetStatus(StarBattleTileStates.STAR)
            newPositions.append(star)
        for noStar in command.GetNoStars():
            self._board[noStar[0]][noStar[1]].SetStatus(StarBattleTileStates.NO_STAR)
            newPositions.append(noStar)

        # Get rid of broken doubles and triples
        unnecessaryDoubles = []
        unnecessaryTriples = []
        for newPosition in newPositions:
            for double in self._doubles:
                if newPosition in double and double not in unnecessaryDoubles:
                    unnecessaryDoubles.append(double)
            for triple in self._triples:
                if newPosition in triple and triple not in unnecessaryTriples:
                    unnecessaryTriples.append(triple)
        for ud in unnecessaryDoubles:
            self._doubles.remove(ud)
        for ut in unnecessaryTriples:
            self._triples.remove(ut)

    def NextSolution(self, tryPuzzleBreak=True):
        """
        Try to compute the next solution.

        :param tryPuzzleBreak: If True try to break the puzzle via brute force if there is not
        other way
        :type tryPuzzleBreak: bool
        :return: command
        :rtype: StarBattleCommand or None
        """
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
            for depth in range(30):
                command = self.TryPuzzleBreak(depth)
                if command:
                    return command

    def GetSingleDimensionCommand(self, getter, d, commandType):
        """
        Check a single row/column/area for forced solutions. If there are any return a command

        :param getter: Function to get a specific row/column/area
        :type getter: function
        :param d: index (for rows/columns) or key for areas
        :type d: int or str
        :param commandType: Set the command type (e.g. R, C, A)
        :type commandType: str
        :return: command
        :rtype: StarBattleCommand or None
        """
        positions = getter(d, [StarBattleTileStates.UNKNOWN, StarBattleTileStates.STAR])
        solutions = self.GetPossibleSolutions(positions)
        command = self.InterpretSolutions(solutions)
        if command:
            command.SetType("{0}{1}".format(commandType, d))
            return command
        return None

    def GetMultiDimensionCommand(self, getter, commandType):
        """
        Check multiple rows/columns for forced solution. If there are any return a command

        :param getter: Function to get a specific row/column/area
        :type getter: function
        :param commandType: Set the command type (e.g. R, C, A)
        :type commandType: str
        :return: command
        :rtype: StarBattleCommand or None
        """
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

    def TryPuzzleBreak(self, depth):
        """
        This algorythm trys to break the puzzle via brute force:

        1) Get all unknown positions
        2) Save the state of the current board
        3) Pick a position and put a "Star" in it
        4) Call NextSolution up to [depth] times. There can be 3 things that happen:
        4a) The grid is broken --> Now we know for sure that this position can't be a star --> 5)
        4b) The grid is solved --> We wanted to break the puzzle --> reset board from temp and 3)
        4c) The grid is neither solved nor broken --> reset board from temp and 3)
        5) reset board, return new command(pos = NoStar) + commands that prove the statement

        :param depth: number of NextSolution steps the algorithm trys
        :type depth: int
        :return: command
        :rtype: StarBattleCommand or None
        """
        unknownPositions = []
        for r in range(self._dimension):
            for c in range(self._dimension):
                if self._board[r][c].Status() == StarBattleTileStates.UNKNOWN:
                    unknownPositions.append((r, c))

        boardTemp, doublesTemp, triplesTemp = self.CopyBoard(self._board, self._doubles,
                                                             self._triples, self._dimension)
        breakCommand = None
        for pos in unknownPositions:
            # reset board
            self._board, self._doubles, self._triples = self.CopyBoard(boardTemp, doublesTemp,
                                                                       triplesTemp, self._dimension)
            isBroken = False
            newStar = [pos]
            newNoStars = []
            for noStar in self.GetAdjacentPositions(pos, self._dimension):
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
                                                                   triplesTemp, self._dimension)
        return breakCommand

    def InterpretSolutions(self, solutions):
        """
        Interpret all possible solutions and return a command

        :param solutions: all possible solutions
        :type solutions: list(dict)
        :return: command
        :rtype: StarBattleCommand or None
        """
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

    def GetForcedSolutions(self, solutions, key, flt):
        """
        Find forced solutions in the possible solutions e.g. stars/noStars that are in all possible
        solutions.

        :param solutions: all possible solutions
        :type solutions: dict
        :param key: star/noStar
        :type key: str
        :param flt: tile filter
        :type flt: list(StarBattleTileStates)
        :return: positions of forced solutions
        :rtype: list(tuple(int, int))
        """
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

    def GetDoubles(self, solutions, key, flt):
        """
        Find doubles - two connected positions where one of them are in every possible solution.

        :param solutions: all possible solutions
        :type solutions: list(dict)
        :param key: star/noStar
        :type key: str
        :param flt: tile filter
        :type flt: list(StarBattleTileStates)
        :return: positions of forced solutions
        :rtype: list(tuple(int, int))
        """
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
        """
        Find triples - three connected positions where one of them are in every possible solution.

        :param solutions: all possible solutions
        :type solutions: list(dict)
        :param key: star/noStar
        :type key: str
        :param flt: tile filter
        :type flt: list(StarBattleTileStates)
        :return: positions of forced solutions
        :rtype: list(tuple(int, int))
        """
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

    def GetPossibleSolutions(self, positions):
        """
        Compute every possible solution (stars, noStars) while considering the star battle rules.
        Apply special logic by considering doubles and triples.

        :param positions: list of positions that should be investigated
        :type positions: list(tuple(int,int))
        :return: list of possible solutions
        :rtype: list(dict)
        """
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

    def GetNoStarsFromForcedSolutions(self, forcedSolutions, unknownPositions, starCount):
        """
        Special logic by considering doubles and triples. These may force special constraints.

        :param forcedSolutions: doubles/triples
        :type forcedSolutions: list(list(int, int))
        :param unknownPositions: positons without a star
        :type unknownPositions: list(tuple(int, int))
        :param starCount: number of stars in this area
        :type starCount: int
        :return: list of noStar postions
        :rtype: list(tuple(int, int))
        """
        filteredForcedSolutions = []
        for forcedSolution in forcedSolutions:
            for pos in forcedSolution:
                if pos not in unknownPositions:
                    break
            else:
                filteredForcedSolutions.append(forcedSolution.copy())

        newFilteredPositions = []
        if len(filteredForcedSolutions) + starCount == self._stars:
            for pos in unknownPositions:
                for forcedSolution in filteredForcedSolutions:
                    if pos in forcedSolution:
                        break
                else:
                    newFilteredPositions.append(pos)
        return newFilteredPositions

    def _GetPossibleSolutionsRecursive(self, filteredPositions, stars, noStars=None,
                                       solutions=None):
        """
        Recursive function. Compute every possible solution (stars, noStars) while considering the
        star battle rules.

        :param filteredPositions: list of positions that should be investigated
        :type filteredPositions: list(tuple(int,int))
        :param stars: list of star positions
        :type stars: list(tuple(int,int))
        :param noStars: list of noStar positions
        :type noStars: list(tuple(int,int))
        :param solutions: list of possible solutions (give to sub call)
        :type solutions: list(dict)
        :return: list of possible solutions
        :rtype: list(dict)
        """
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
            for noStar in self.GetAdjacentPositions(pos, self._dimension):
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

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

    def __init__(self, gridData, dimension, stars):
        returnCode = StarBattleSolver.IsValidStarBattleGrid(gridData, dimension, stars)
        if returnCode != StarBattleGridCodes.OK:
            raise StarBattleSolverError("Invalid BattleSolver grid: {0}".format(returnCode.name))

        self._dimension = dimension
        self._stars = stars
        self._gridData = gridData


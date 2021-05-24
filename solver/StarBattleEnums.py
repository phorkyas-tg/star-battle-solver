from enum import Enum


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

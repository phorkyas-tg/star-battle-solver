import unittest
import copy

from solver.StarBattleSolver import StarBattleSolver, StarBattleGridCodes


class StarBattleSolverTest(unittest.TestCase):

    @staticmethod
    def GetValidDict():
        mockDict = {}
        for i in range(9):
            mockDict.setdefault(str(i), [])
            for c in range(9):
                mockDict[str(i)].append((i, c))
        return mockDict

    def testGridInvalidCellCount(self):
        mockDict = {}
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDict),
                         StarBattleGridCodes.INVALID_CELL_COUNT)
        mockDict = {"1": [0] * 82}
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDict),
                         StarBattleGridCodes.INVALID_CELL_COUNT)

    def testGridInvalidAreaCount(self):
        mockDict = {"1": [0]*81}
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDict),
                         StarBattleGridCodes.INVALID_AREA_COUNT)

    def testInvalidAreaSize(self):
        mockDict = self.GetValidDict()
        for i in range(7):
            mockDict["1"].append(mockDict["0"].pop(0))

        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDict),
                         StarBattleGridCodes.INVALID_AREA_SIZE)

    def testGridDuplicatePositions(self):
        mockDict = self.GetValidDict()
        mockDict["0"][0] = (0, 1)
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDict),
                         StarBattleGridCodes.DUPLICATE_POSITION)

    def testGridInvalidDimension(self):
        mockDict = self.GetValidDict()

        mockDictTemp = copy.deepcopy(mockDict)
        mockDictTemp["0"][0] = (0, -1)
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDictTemp),
                         StarBattleGridCodes.INVALID_DIMENSION)

        mockDictTemp = copy.deepcopy(mockDict)
        mockDictTemp["0"][0] = (-1, 0)
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDictTemp),
                         StarBattleGridCodes.INVALID_DIMENSION)

        mockDictTemp = copy.deepcopy(mockDict)
        mockDictTemp["0"][0] = (0, 9)
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDictTemp),
                         StarBattleGridCodes.INVALID_DIMENSION)

        mockDictTemp = copy.deepcopy(mockDict)
        mockDictTemp["0"][0] = (9, 0)
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDictTemp),
                         StarBattleGridCodes.INVALID_DIMENSION)

    def testValidGrid(self):
        mockDict = self.GetValidDict()
        self.assertEqual(StarBattleSolver.IsValidStarBattleGrid(mockDict),
                         StarBattleGridCodes.OK)

    def testGridIsAdjacent(self):
        pos1 = (0, 0)
        pos2 = (1, 0)
        pos3 = (0, 1)
        pos4 = (1, 1)
        pos5 = (1, 2)

        self.assertFalse(StarBattleSolver.IsAdjacent(pos1, pos1, checkDiagonal=True))
        self.assertTrue(StarBattleSolver.IsAdjacent(pos1, pos2, checkDiagonal=True))
        self.assertTrue(StarBattleSolver.IsAdjacent(pos1, pos3, checkDiagonal=True))
        self.assertTrue(StarBattleSolver.IsAdjacent(pos1, pos4, checkDiagonal=True))
        self.assertFalse(StarBattleSolver.IsAdjacent(pos1, pos5, checkDiagonal=True))

        self.assertFalse(StarBattleSolver.IsAdjacent(pos1, pos1, checkDiagonal=False))
        self.assertTrue(StarBattleSolver.IsAdjacent(pos1, pos2, checkDiagonal=False))
        self.assertTrue(StarBattleSolver.IsAdjacent(pos1, pos3, checkDiagonal=False))
        self.assertFalse(StarBattleSolver.IsAdjacent(pos1, pos4, checkDiagonal=False))
        self.assertFalse(StarBattleSolver.IsAdjacent(pos1, pos5, checkDiagonal=False))

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

    @staticmethod
    def GetEasyLevel():
        return {"1": [[0, 0], [0, 1], [0, 2], [1, 0]],
                "2": [[0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8],
                      [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8]],
                "7": [[1, 1], [1, 2], [2, 0], [2, 1], [2, 2], [2, 3],
                      [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1],
                      [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [5, 2], [5, 3]],
                "4": [[2, 4], [2, 5], [2, 6], [2, 7], [3, 5], [3, 6],
                      [3, 7], [4, 7], [5, 7], [5, 8], [6, 8], [7, 8], [8, 8]],
                "3": [[2, 8], [3, 8], [4, 8]],
                "8": [[4, 0], [5, 0], [5, 1], [6, 0], [6, 1], [6, 2], [6, 3],
                      [7, 1], [7, 2], [7, 3], [7, 4], [8, 3], [8, 4], [8, 5]],
                "6": [[5, 4], [5, 5], [5, 6], [6, 4], [6, 5], [6, 6],
                      [7, 5], [7, 6], [8, 6]],
                "5": [[6, 7], [7, 7], [8, 7]],
                "0": [[7, 0], [8, 0], [8, 1], [8, 2]]}

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

    def testNextEasyLevel(self):
        easyLevel = self.GetEasyLevel()
        solver = StarBattleSolver(easyLevel, 9, 2, True)
        command = solver.NextSolution()
        self.assertEqual(str(command),
                         "stars: [(2, 8), (4, 8)] | "
                         "noStars [(1, 7), (1, 8), (2, 7), (3, 7), (3, 8), (4, 7), (5, 7), (5, 8)]")
        solver.Commit(command)

        command = solver.NextSolution()
        self.assertEqual(str(command),
                         "stars: [(2, 8), (4, 8)] | "
                         "noStars [(0, 8), (6, 8), (7, 8), (8, 8)]")
        solver.Commit(command)

        command = solver.NextSolution()
        self.assertEqual(str(command),
                         "stars: [(6, 7), (8, 7)] | "
                         "noStars [(5, 6), (5, 7), (5, 8), (6, 6), (6, 8), (7, 6), "
                         "(7, 7), (7, 8), (8, 6), (8, 8)]")
        solver.Commit(command)

        command = solver.NextSolution()
        self.assertEqual(str(command),
                         "stars: [(6, 7), (8, 7)] | "
                         "noStars [(0, 7)]")
        solver.Commit(command)

        command = solver.NextSolution()
        print(str(command))

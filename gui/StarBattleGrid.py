import wx
import wx.grid as gridlib
import random

from solver.StarBattleSolver import StarBattleCommand


class StarBattleGrid(gridlib.Grid):
    def __init__(self, parent, dimension):
        gridlib.Grid.__init__(self, parent)

        self.CreateGrid(dimension, dimension)
        self.SetDefaultRowSize(50, True)
        self.SetDefaultColSize(50, True)
        self.DisableDragGridSize()
        self.HideRowLabels()
        self.HideColLabels()

        self._dimension = dimension
        self._selectedCells = []

        for r in range(self._dimension):
            for c in range(self._dimension):
                self.SetReadOnly(r, c)

        # Event bindings
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

    def OnRangeSelect(self, evt):
        topLeftCell = evt.GetTopLeftCoords()
        bottomRightCell = evt.GetBottomRightCoords()

        for r in range(topLeftCell.GetRow(), bottomRightCell.GetRow() + 1):
            for c in range(topLeftCell.GetCol(), bottomRightCell.GetCol() + 1):
                if (r, c) not in self._selectedCells and evt.Selecting():
                    self._selectedCells.append((r, c))
                elif (r, c) in self._selectedCells and not evt.Selecting():
                    self._selectedCells.remove((r, c))
        evt.Skip()

    def OnKeyPress(self, evt):
        uk = evt.UnicodeKey

        if uk == 27:
            # Escape
            self._selectedCells = []

        key = chr(evt.UnicodeKey)
        if key != wx.WXK_NONE and key.isalnum():
            for r, c in self._selectedCells:
                self.SetCell(key, r, c)

        evt.Skip()

    def SetCell(self, key, r, c, setColor=True, font=None):
        self.SetCellValue(r, c, key)
        self.SetCellAlignment(r, c, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        if setColor:
            random.seed(hash(key))
            color = wx.Colour(random.randint(0, 255),
                              random.randint(0, 255),
                              random.randint(0, 255))
            self.SetCellBackgroundColour(r, c, color)
        if font:
            self.SetCellFont(r, c, font)
        else:
            self.SetCellFont(r, c, wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

    def Draw(self, command: StarBattleCommand):
        for star in command.GetStars():
            self.SetCell("x", star[0], star[1], False,
                         wx.Font(30, wx.SWISS, wx.NORMAL, wx.BOLD))
        for noStar in command.GetNoStars():
            self.SetCell("o", noStar[0], noStar[1], False,
                         wx.Font(30, wx.SWISS, wx.NORMAL, wx.BOLD))
        for double in command.GetDoubles():
            for pos in double:
                self.SetCell("d", pos[0], pos[1], False,
                             wx.Font(30, wx.SWISS, wx.NORMAL, wx.BOLD))
        for triple in command.GetTriples():
            for pos in triple:
                self.SetCell("t", pos[0], pos[1], False,
                             wx.Font(30, wx.SWISS, wx.NORMAL, wx.BOLD))

    def GetData(self):
        valDict = {}
        for r in range(self._dimension):
            for c in range(self._dimension):
                val = self.GetCellValue(r, c)
                if val:
                    valDict.setdefault(val, [])
                    valDict[val].append((r, c))
        return valDict

    def SetData(self, valDict):
        for key, posList in valDict.items():
            for pos in posList:
                self.SetCell(key, pos[0], pos[1])

    def Clear(self):
        for r in range(self._dimension):
            for c in range(self._dimension):
                self.SetCellValue(r, c, "")
                self.SetCellAlignment(r, c, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellBackgroundColour(r, c, wx.WHITE)

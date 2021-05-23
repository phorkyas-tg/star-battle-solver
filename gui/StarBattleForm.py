import wx
import json
from datetime import datetime

from gui.StarBattleGrid import StarBattleGrid
from solver.StarBattleSolver import StarBattleSolver, StarBattleGridCodes


class StarBattleForm(wx.Frame):
    def __init__(self, dimension=9):
        self.solver = None
        self.dimension = dimension

        wx.Frame.__init__(self, parent=None, title="Star Battle Solver", size=(800, 600))

        self.panel = wx.Panel(self)
        self.sbGrid = StarBattleGrid(self.panel, dimension)

        self.newBtn = wx.Button(self.panel, -1, "NEW")
        self.newBtn.Bind(wx.EVT_BUTTON, self.OnNewBtnClicked)
        self.saveBtn = wx.Button(self.panel, -1, "SAVE")
        self.saveBtn.Bind(wx.EVT_BUTTON, self.OnSaveBtnClicked)
        self.loadBtn = wx.Button(self.panel, -1, "LOAD")
        self.loadBtn.Bind(wx.EVT_BUTTON, self.OnLoadBtnClicked)

        self.stepBtn = wx.Button(self.panel, -1, "STEP")
        self.stepBtn.Bind(wx.EVT_BUTTON, self.OnStepBtnClicked)
        self.solveBtn = wx.Button(self.panel, -1, "SOLVE")
        self.solveBtn.Bind(wx.EVT_BUTTON, self.OnSolveBtnClicked)
        self.cmdArea = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY,
                                   size=wx.Size(dimension * 50, 150))

        # Panel Sizer
        self.mainBox = wx.BoxSizer(wx.VERTICAL)

        self.sbBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sbBoxSizer.Add(self.sbGrid, 1, wx.ALIGN_CENTER | wx.ALL, 5)

        self.buttonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonBoxSizer.Add(self.newBtn, 1, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        self.buttonBoxSizer.Add(self.saveBtn, 1, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        self.buttonBoxSizer.Add(self.loadBtn, 1, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        self.buttonBoxSizer.Add(self.stepBtn, 1, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        self.buttonBoxSizer.Add(self.solveBtn, 1, 1, wx.ALIGN_LEFT | wx.ALL, 5)

        self.consoleSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.consoleSizer.Add(self.cmdArea, 1, 1, wx.ALIGN_LEFT | wx.ALL, 5)

        self.mainBox.Add(self.sbBoxSizer, 1, wx.ALIGN_CENTER, 5)
        self.mainBox.Add(self.buttonBoxSizer, 1, wx.ALIGN_CENTER, 5)
        self.mainBox.Add(self.consoleSizer, 1, wx.ALIGN_CENTER, 5)
        self.panel.SetSizer(self.mainBox)

    def ConsolePrint(self, msgType, msg):
        self.cmdArea.AppendText("{0}: {1}: {2}\n".format(datetime.now().strftime("%H:%M:%S"),
                                                         msgType, msg))

    def OnNewBtnClicked(self, evt):
        self.sbGrid.Clear()

    def OnSaveBtnClicked(self, evt):
        gridData = self.sbGrid.GetData()
        returnCode = StarBattleSolver.IsValidStarBattleGrid(gridData)
        if returnCode != StarBattleGridCodes.OK:
            self.ConsolePrint("ERROR", "Invalid BattleSolver grid: {0}".format(returnCode.name))
            return

        with wx.FileDialog(self, "Save JSON file", wildcard="JSON files (*.json)|*.json",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    json.dump(gridData, file)
            except IOError:
                self.ConsolePrint("ERROR", "Can't save json to path: {0}".format(pathname))
        self.ConsolePrint("INFO", "Saved json to path: {0}".format(pathname))
        self.solver = StarBattleSolver(gridData, self.dimension)

    def OnLoadBtnClicked(self, evt):
        with wx.FileDialog(self, "Open JSON file", wildcard="JSON files (*.json)|*.json",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    gridData = json.load(file)

                    returnCode = StarBattleSolver.IsValidStarBattleGrid(gridData)
                    if returnCode != StarBattleGridCodes.OK:
                        self.ConsolePrint("ERROR",
                                          "Invalid File: {0}".format(returnCode.name))
                        return
                    self.sbGrid.SetData(gridData)
                    self.solver = StarBattleSolver(gridData, self.dimension)
            except IOError:
                self.ConsolePrint("ERROR", "Can't open json: {0}".format(pathname))
            self.ConsolePrint("INFO", "Opened json: {0}".format(pathname))

    def Next(self):
        command = self.solver.NextSolution()
        if command is None:
            return False
        self.solver.Commit(command)
        self.sbGrid.Draw(command)
        self.ConsolePrint("STEP", str(command))

        solved, broken = self.solver.GetStatus()
        if solved:
            self.ConsolePrint("INFO", "Grid is solved!")
        if broken:
            self.ConsolePrint("ERROR", "Grid is broken!")

        return True

    def OnStepBtnClicked(self, evt):
        if not self.Next():
            self.ConsolePrint("INFO", "No solution found")

    def OnSolveBtnClicked(self, evt):
        while self.Next():
            pass

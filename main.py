import wx

from gui.StarBattleForm import StarBattleForm

if __name__ == '__main__':
    app = wx.App()
    frm = StarBattleForm()
    frm.Show()
    app.MainLoop()

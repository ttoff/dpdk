# PackItem
# Created by drewc on 5/30/2023 7:10 PM
# widget to display each available pack

import json

import wx
from wx import Window

from src.base import DPDKGlobal


class PackItem(wx.Panel):

    def __init__(self, packFolder: str, parent: Window, sdkInterface, id: int = wx.ID_ANY, name: str = "packitem"):
        super().__init__(parent, id, wx.DefaultPosition, (480, 40), wx.BORDER_THEME, name = name)

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.sdkInterface = sdkInterface

        self.packFolder: str = packFolder
        try:
            with open(f'sdk/packs/{packFolder}/pack.json') as file:
                jsFile = json.loads(file.read())

            packNameLabel = wx.StaticText(
                self, label = f"{jsFile.get('pack_name')} (by {jsFile.get('pack_author')})"
            )
            packNameLabel.SetFont(sdkInterface.uiFontNormal)
            packPathLabel = wx.StaticText(
                self, label = f'/{packFolder}'
            )

            choosePackButton = wx.Button(self, label = 'Open', pos = (380, 5))
            choosePackButton.Bind(wx.EVT_BUTTON, self.loadPack)

            self.layout.AddMany((
                packNameLabel,
                packPathLabel,
            ))
            self.SetSizer(self.layout)
        except:
            DPDKGlobal.DKBase.notify.warning(f'There was an error loading pack information for /{packFolder}.'
                                             f'Make sure pack.json exists and is formatted correctly.')
            self.delete(_)
            return

    def loadPack(self, _):
        return

    def delete(self, _):
        self.sdkInterface.packListItems.remove(self)
        self.sdkInterface.refreshPackList()
        self.Destroy()

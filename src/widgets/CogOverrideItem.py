# PackItem
# Created by drewc on 5/30/2023 7:10 PM
# widget to display each available pack

import json

import wx
from wx import Window

from src.base import DPDKGlobal
from src.datapack.DataPackManager import DataPackManager


class CogOverrideItem(wx.Panel):

    def __init__(self, overrideName: str, parent: Window, sdkInterface, id: int = wx.ID_ANY, name: str = "cog"):
        super().__init__(parent, id, wx.DefaultPosition, parent.FromDIP(wx.Size((280, 40))), wx.BORDER_THEME, name = name)

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.sdkInterface = sdkInterface

        self.overrideName: str = overrideName

        packFolder: str = DPDKGlobal.DKBase.activePack
        try:
            with open(f'sdk/packs/{packFolder}/cogs/appearance/{overrideName}') as file:
                jsFile = json.loads(file.read())

            cogNameLabel = wx.StaticText(
                self, label = f"{DataPackManager.getLocalizedText(jsFile.get('name'))}"
            )
            cogNameLabel.SetFont(sdkInterface.uiFontNormal)
            cogPathLabel = wx.StaticText(
                self, label = overrideName
            )

            choosePackButton = wx.Button(self, label = 'Open', pos = self.FromDIP(wx.Point(200, 5)))
            choosePackButton.Bind(wx.EVT_BUTTON, self.loadCog)

            self.layout.AddMany((
                cogNameLabel,
                cogPathLabel,
            ))
            self.SetSizer(self.layout)
        except:
            DPDKGlobal.DKBase.notify.warning(f'There was an error loading information for /{packFolder}.'
                                             f'Make sure it is formatted correctly.')
            self.delete()
            return

    def loadCog(self, _):
        self.sdkInterface.loadCogFile(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/{self.overrideName}')

    def delete(self, _ = None):
        self.Destroy()

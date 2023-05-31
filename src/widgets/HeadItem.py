from os.path import abspath, relpath
from pathlib import Path
from typing import List

import wx
from panda3d.core import Vec3, Vec4, LVector3, LVector3f, Vec3F, VBase3, VBase3F, VBase4F
from wx import Window, FileDirPickerEvent
from wx.lib.agw.cubecolourdialog import CubeColourDialog
from wx.lib.agw.floatspin import FloatSpin
from wx.lib.agw.knobctrl import KnobCtrl

from src.base import DPDKGlobal
from src.base.ToontownTypes import TCogHead


class HeadItem(wx.Panel):

    def __init__(self, parent: Window, sdkInterface, id: int = wx.ID_ANY, name: str = "Head"):
        super().__init__(parent, id, wx.DefaultPosition, parent.FromDIP(wx.Size((400, 230))), wx.BORDER_THEME, name = name)

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.sdkInterface = sdkInterface

        self.modelPath: str = ''
        self.modelNode: str = ''
        self.removeNodes: List[str] = []
        self.texture: str = ''
        self.pos: VBase3F = Vec3(0, 0, 0)
        self.hpr: VBase3F = Vec3(0, 0, 0)
        self.scale: VBase3F = Vec3(1, 1, 1)
        self.colorScale: VBase4F = Vec4(1, 1, 1, 1)

        deleteButton = wx.Button(self, label = 'X', pos = self.FromDIP(wx.Point(380, 0)), size = self.FromDIP(wx.Size((15, 15))))
        deleteButton.Bind(wx.EVT_BUTTON, self.delete)

        pathEntryLabel = wx.StaticText(
            self, label = 'Model File'
        )
        self.pathEntry = wx.FilePickerCtrl(
            self,
            size = self.FromDIP(wx.Size((400, 25))),
            wildcard = "Realms Model Files (*.bam)|*.bam",
            message = "Select a model file"
        )
        self.pathEntry.SetInitialDirectory(abspath(DPDKGlobal.DKBase.gameResourcesPath))
        self.pathEntry.Bind(wx.EVT_FILEPICKER_CHANGED, self.setModelPath)

        nodeEntryLabel = wx.StaticText(
            self, label = 'Find Sub Node (Optional)'
        )

        self.nodeEntry = wx.TextCtrl(
            self, size = self.FromDIP(wx.Size((400, 25))),
        )
        self.nodeEntry.Bind(wx.EVT_TEXT, self.__setNode)

        textureEntryLabel = wx.StaticText(
            self, label = 'Texture Override (Optional)'
        )
        self.textureEntry = wx.FilePickerCtrl(
            self,
            size = self.FromDIP(wx.Size((400, 25))),
            wildcard = "Realms Texture Files (*.png)|*.png",
            message = "Select a texture file"
        )
        self.textureEntry.SetInitialDirectory(abspath(DPDKGlobal.DKBase.gameResourcesPath))
        self.textureEntry.Bind(wx.EVT_FILEPICKER_CHANGED, self.setTexturePath)

        self.posBox = wx.Panel(self)
        posBoxLayout = wx.BoxSizer(wx.HORIZONTAL)

        posLabel = wx.StaticText(self.posBox, size = self.FromDIP(wx.Size(100, 25)), label = 'Position')

        self.posX = FloatSpin(self.posBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -200, max_val = 200, increment = 0.01, value = 0.0, digits = 8)
        self.posX.Bind(wx.EVT_SPINCTRL, self.__setPosX)

        self.posY = FloatSpin(self.posBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -200, max_val = 200, increment = 0.01, value = 0.0, digits = 8)
        self.posY.Bind(wx.EVT_SPINCTRL, self.__setPosY)

        self.posZ = FloatSpin(self.posBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -200, max_val = 200, increment = 0.01, value = 0.0, digits = 8)
        self.posZ.Bind(wx.EVT_SPINCTRL, self.__setPosZ)

        posBoxLayout.AddMany((
            posLabel,
            self.posX,
            self.posY,
            self.posZ,
        ))
        self.posBox.SetSizer(posBoxLayout)

        self.hprBox = wx.Panel(self)
        hprBoxLayout = wx.BoxSizer(wx.HORIZONTAL)

        hprLabel = wx.StaticText(self.hprBox, size = self.FromDIP(wx.Size(100, 25)), label = 'Rotation')
        self.h = FloatSpin(self.hprBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -360, max_val = 360, increment = 1, value = 0.0, digits = 3)
        self.h.Bind(wx.EVT_SPINCTRL, self.__setH)

        self.p = FloatSpin(self.hprBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -360, max_val = 360, increment = 1, value = 0.0, digits = 3)
        self.p.Bind(wx.EVT_SPINCTRL, self.__setP)

        self.r = FloatSpin(self.hprBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -360, max_val = 360, increment = 1, value = 0.0, digits = 3)
        self.r.Bind(wx.EVT_SPINCTRL, self.__setR)

        hprBoxLayout.AddMany((
            hprLabel,
            self.h,
            self.p,
            self.r
        ))
        self.hprBox.SetSizer(hprBoxLayout)

        self.scaleBox = wx.Panel(self)
        scaleBoxLayout = wx.BoxSizer(wx.HORIZONTAL)

        scaleLabel = wx.StaticText(self.scaleBox, size = self.FromDIP(wx.Size(100, 25)), label = 'Scale')
        self.sx = FloatSpin(self.scaleBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -100, max_val = 100, increment = 0.01, value = 1.0, digits = 4)
        self.sx.Bind(wx.EVT_SPINCTRL, self.__setScaleX)

        self.sy = FloatSpin(self.scaleBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -100, max_val = 100, increment = 0.01, value = 1.0, digits = 4)
        self.sy.Bind(wx.EVT_SPINCTRL, self.__setScaleY)

        self.sz = FloatSpin(self.scaleBox, size = self.FromDIP(wx.Size(100, 25)), min_val = -100, max_val = 100, increment = 0.01, value = 1.0, digits = 4)
        self.sz.Bind(wx.EVT_SPINCTRL, self.__setScaleZ)

        scaleBoxLayout.AddMany((
            scaleLabel,
            self.sx,
            self.sy,
            self.sz
        ))
        self.scaleBox.SetSizer(scaleBoxLayout)

        self.colorBox = wx.Panel(self)
        colorBoxLayout = wx.BoxSizer(wx.HORIZONTAL)

        self.colorLabel = wx.StaticText(self.colorBox, size = self.FromDIP(wx.Size(300, 25)), label = 'Color (1.0, 1.0, 1.0, 1.0)')
        self.colorPicker = CubeColourDialog(self.colorBox)
        colorButton = wx.Button(self.colorBox, label = 'Choose Color', size = self.FromDIP(wx.Size(100, 25)))
        colorButton.Bind(wx.EVT_BUTTON, self.__openColorPicker)

        colorBoxLayout.AddMany((
            self.colorLabel,
            colorButton
        ))
        self.colorBox.SetSizer(colorBoxLayout)

        self.layout.AddMany((
            pathEntryLabel,
            self.pathEntry,
            nodeEntryLabel,
            self.nodeEntry,
            textureEntryLabel,
            self.textureEntry,
            self.posBox,
            self.hprBox,
            self.scaleBox,
            self.colorBox
        ))
        self.SetSizer(self.layout)

    def setInitial(self, path: str, node: str,
                   texture: str, pos: Vec3, hpr: Vec3, scale: Vec3, colorScale: Vec3, removeNodes: List[str]):
        self.modelPath = path
        self.pathEntry.SetPath(self.modelPath)
        self.modelNode = node
        self.nodeEntry.SetValue(self.modelNode)
        self.texture = texture
        self.textureEntry.SetPath(self.texture)
        self.pos = Vec3(*pos)
        self.posX.SetValue(pos[0])
        self.posY.SetValue(pos[1])
        self.posZ.SetValue(pos[2])
        self.hpr = Vec3(*hpr)
        self.h.SetValue(hpr[0])
        self.p.SetValue(hpr[1])
        self.r.SetValue(hpr[2])
        self.scale = Vec3(*scale)
        self.sx.SetValue(scale[0])
        self.sy.SetValue(scale[1])
        self.sz.SetValue(scale[2])
        self.colorScale = Vec4(*colorScale)
        self.__setColor(*colorScale)
        self.removeNodes = removeNodes

    def setTexturePath(self, e: FileDirPickerEvent):
        if not e.GetPath():
            phaseLocation = ''
        else:
            phaseLocation = Path(relpath(e.GetPath(), DPDKGlobal.DKBase.gameResourcesPath)).as_posix()
        if not phaseLocation.startswith('.'):
            self.textureEntry.SetPath(phaseLocation)
            self.texture = phaseLocation
        else:
            self.texture = e.GetPath()

    def setModelPath(self, e: FileDirPickerEvent):
        if not e.GetPath():
            phaseLocation = ''
        else:
            phaseLocation = Path(relpath(e.GetPath(), DPDKGlobal.DKBase.gameResourcesPath)).as_posix()
        if not phaseLocation.startswith('.'):
            self.pathEntry.SetPath(phaseLocation)
            self.modelPath = phaseLocation
        else:
            self.modelPath = e.GetPath()

    def __setNode(self, _):
        self.modelNode = self.nodeEntry.GetValue()

    def __setPosX(self, _):
        self.pos.setX(self.posX.GetValue())

    def __setPosY(self, _):
        self.pos.setY(self.posY.GetValue())

    def __setPosZ(self, _):
        self.pos.setZ(self.posZ.GetValue())

    def __setH(self, _):
        self.hpr.setX(self.h.GetValue())

    def __setP(self, _):
        self.hpr.setY(self.p.GetValue())

    def __setR(self, _):
        self.hpr.setZ(self.r.GetValue())

    def __setScaleX(self, _):
        self.scale.setX(self.sx.GetValue())

    def __setScaleY(self, _):
        self.scale.setY(self.sy.GetValue())

    def __setScaleZ(self, _):
        self.scale.setZ(self.sz.GetValue())

    def __openColorPicker(self, _):
        if self.colorPicker.ShowModal() == wx.ID_OK:
            colorData = self.colorPicker.GetColourData()
            color = colorData.GetColour()
            r, g, b, a = color.Red() / 255., color.Green() / 255., color.Blue() / 255., color.Alpha() / 255.
            self.__setColor(r, g, b, a)

    def __setColor(self, r, g, b, a):
        self.colorLabel.SetLabel(f'Color ({r:.06f}, {g:.06f}, {b:.06f}, {a:.06f})')
        self.colorScale = Vec4(r, g, b, a)

    def delete(self, _ = None):
        self.sdkInterface.headItems.remove(self)
        self.sdkInterface.updateHeads(_)
        self.sdkInterface.refreshHeadList()
        self.Destroy()

    def get(self) -> TCogHead:
        return (
            self.modelPath,
            self.modelNode,
            self.texture,
            self.pos,
            self.hpr,
            self.scale,
            self.colorScale,
            self.removeNodes
        )

import subprocess

import shutil

import glob
import json
import os
from os.path import abspath, relpath
from pathlib import PurePosixPath, Path
from typing import List, Dict

import wx
from wx import CommandEvent
from wx.lib.agw import fourwaysplitter as FWS
from wx.lib.agw.cubecolourdialog import CubeColourDialog
from wx.lib.agw.floatspin import FloatSpin

from panda3d.core import *
from direct.showbase.ShowBase import *
from direct.showbase import ShowBaseGlobal
from direct.directtools.DirectGlobals import *
from wx.lib.agw.knobctrl import KnobCtrl, EVT_KC_ANGLE_CHANGED, KnobCtrlEvent
from wx.lib.agw.ribbon import RibbonBar, RibbonPage
from wx.lib.scrolledpanel import ScrolledPanel

from .WxAppShell import *
from .ViewPort import *
from src.base import DPDKGlobal
from ..datapack.DataPackManager import DataPackManager
from ..ott.OTTUtil import toAlphaNumeric
from ..pandaview.Cog import Cog
from ..widgets.CogOverrideItem import CogOverrideItem
from ..widgets.PackItem import PackItem
from ..widgets.HeadItem import HeadItem


class WxPandaShell(WxAppShell):
    """ Class for Panda3D LevelEditor """
    frameWidth = 1280
    frameHeight = 720
    appversion = '1.0'
    appname = 'Toontown Realms Data Pack Development Kit'
    copyright = ('Copyright 2023 Toontown Realms.' +
                 '\nAll Rights Reserved.')

    def __init__(self):
        self.packListItems: List[PackItem] = []
        self.headItems: List[HeadItem] = []
        self.cogOverrideItems: List[CogOverrideItem] = []

        WxAppShell.__init__(self)

        self.Size = self.FromDIP(wx.Size(self.frameWidth, self.frameHeight))

        self.initialize()

        wx.MessageBox(
            """Welcome to the Toontown Realms Data Pack Development Kit!
        
This is ALPHA software. Be sure to make regular backups of your Data Pack files. Most changes are applied automatically with no way to revert.""",
            caption = "Notice")

    def createInterface(self):
        self.uiFontLarge = wx.Font(26, family = wx.FONTFAMILY_DEFAULT, style = 0, weight = 90)
        self.uiFontNormal = wx.Font(12, family = wx.FONTFAMILY_DEFAULT, style = 0, weight = 90)
        self.tabFrame = wx.Notebook(self)

        self.shareMenu = wx.Menu()
        self.menuBar.Insert(1, self.shareMenu, "&Share")
        self.compileButton: wx.MenuItem = wx.MenuItem(self.shareMenu, wx.ID_SAVE, text = 'Compile Pack', kind = wx.ITEM_NORMAL)
        self.shareMenu.Append(self.compileButton)

        self.Bind(wx.EVT_MENU, self.buildPack, self.compileButton)
        self.compileButton.Enable(0)

        self.setupHomePage()

        self.setupCogEditorPage()

        self.setupSettingsPage()

        # add the pages

        self.Layout()
        self.tabFrame.AddPage(self.homeFrame, "Home")
        self.tabFrame.AddPage(self.settingsPage, "Settings")

    def buildPack(self, _ = None):
        if not os.path.exists('sdk/built'):
            os.makedirs('sdk/built')
        mf: Multifile = Multifile()
        mf.openWrite(f'sdk/built/{DPDKGlobal.DKBase.activePack}.rmdp')

        files = glob.glob(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/**/*.*', recursive = True)
        for i in files:
            i = i.replace("\\", "/")
            i = str(PurePosixPath(i))
            subfilename = i.replace(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/', '')
            fn = Filename(i)
            fn.setBinary()
            mf.addSubfile(subfilename, fn, 8)

        mf.flush()
        mf.close()
        folder = abspath(f'sdk/built/{DPDKGlobal.DKBase.activePack}.rmdp')
        subprocess.run(f'explorer /select, "{folder}"')

    def setupHomePage(self):
        # === Home Page ===
        self.homeFrame = wx.Panel(self.tabFrame)
        layout = wx.BoxSizer(wx.VERTICAL)
        self.homeFrame.SetSizer(layout)

        availPacksLabel = wx.StaticText(self.homeFrame, label = 'Available Datapacks')
        availPacksLabel.SetFont(self.uiFontLarge)
        layout.Add(availPacksLabel)

        self.availPacksList = ScrolledPanel(self.homeFrame, size = self.FromDIP(wx.Size(500, 500)))

        self.availPackLayout = wx.BoxSizer(wx.VERTICAL)

        self.availPacksList.SetSizer(self.availPackLayout)
        self.availPacksList.SetupScrolling()

        layout.Add(self.availPacksList)

        newPackButton = wx.Button(self.homeFrame, label = 'New Pack')
        newPackButton.Bind(wx.EVT_BUTTON, self.newPack)
        layout.Add(newPackButton)
        self.updatePackList()

    def updatePackList(self):
        for pack in self.packListItems:
            pack.delete()
        self.packListItems = []

        if not os.path.exists('sdk/packs'):
            os.mkdir('sdk/packs')

        for folder in os.listdir('sdk/packs'):
            if os.path.exists(f'sdk/packs/{folder}/pack.json'):
                self.packListItems.append(PackItem(
                    packFolder = folder,
                    parent = self.availPacksList,
                    sdkInterface = self
                ))

        self.refreshPackList()

    def refreshPackList(self):
        self.availPackLayout.Clear()
        for pack in self.packListItems:
            self.availPackLayout.Add(pack)
        self.availPacksList.SetupScrolling()

    def newPack(self, _ = None):
        dialog: wx.Dialog
        with wx.Dialog(parent = self, title = 'Create a Datapack', style = wx.CAPTION) as dialog:
            lpackfilename = wx.StaticText(dialog, label = 'Pack Filename')
            packfilename = wx.TextCtrl(dialog)

            def handlePackKeypress(event):
                keycode = event.GetKeyCode()
                if chr(keycode).isalnum() or keycode in (8, 95, 45, 32):
                    event.Skip()

            packfilename.Bind(wx.EVT_CHAR, handlePackKeypress)
            lpackname = wx.StaticText(dialog, label = 'Pack Name')
            packname = wx.TextCtrl(dialog)
            packauthor = wx.TextCtrl(dialog)
            lpackauthor = wx.StaticText(dialog, label = 'Pack Author')
            createButton = wx.Button(dialog, id= wx.ID_OK, label = 'Create')
            cancelButton = wx.Button(dialog, id = wx.ID_CANCEL, label = 'Cancel')

            dialLayout = wx.BoxSizer(wx.VERTICAL)
            dialLayout.AddMany((lpackfilename, packfilename, lpackname, packname, lpackauthor, packauthor, createButton, cancelButton))
            dialog.SetSizer(dialLayout)

            if dialog.ShowModal() == wx.ID_OK:
                _packfn: str = packfilename.GetValue()
                _packname: str = packname.GetValue()
                _packauthor: str = packauthor.GetValue()
                if any(x == '' for x in (_packfn, _packname, _packauthor)):
                    wx.MessageBox('You must fill out all the available fields')
                    self.newPack(None)
                    return
                if os.path.exists(f'sdk/packs/{_packfn}'):
                    wx.MessageBox(f'A pack with this filename ({_packfn}) already exists')
                    self.newPack(None)
                    return
                os.makedirs(f'sdk/packs/{_packfn}')
                packinfo = {
                    "pack_name": _packname,
                    "pack_author": _packauthor,
                    "datapacks_version": 100,
                    "pack_identifier": f"{toAlphaNumeric(_packauthor.lower())}:{toAlphaNumeric(_packname.lower())}"
                }
                with open(f'sdk/packs/{_packfn}/pack.json', 'w') as info:
                    json.dump(packinfo, info, indent = 4)
                self.openPack(_packfn)

    def openPack(self, packPath: str):
        DPDKGlobal.DKBase.activePack = packPath
        self.loadPack(None)

    def loadPack(self, _):
        self.compileButton.Enable(1)
        for i in range(self.tabFrame.GetPageCount()):
            self.tabFrame.RemovePage(0)
        self.tabFrame.AddPage(self.cogEditorFrame, "Cog Appearances")
        self.updateOverrides()

        self.tabFrame.AddPage(self.settingsPage, "Settings")

    def setupCogEditorPage(self):
        # === Cog Editor ===
        self.cogEditorFrame = wx.SplitterWindow(self.tabFrame, style = wx.SP_3D | wx.SP_BORDER)
        self.cogEditorFrame.Hide()

        self.cogEditorFileBar = wx.Panel(self.cogEditorFrame)
        wx.StaticText(self.cogEditorFileBar, label = "Cog")

        self.viewport = Viewport.makePerspective(self.cogEditorFrame, pos = Point3(0, -20, 5), hpr = Point3(0, 0, 0))
        self.cogEditorRight = wx.Notebook(self.cogEditorFrame)
        self.cogEditorFrame.SplitVertically(self.viewport, self.cogEditorRight, 500)

        self.cogPreview = Cog()
        self.cogPreview.reparentTo(render)
        self.cogPreview.setZ(0)
        self.cogPreview.setH(180)

        self.cogPreview.hide()

        # == BODY TYPE ==
        self.cogEditorTabBody = wx.Panel(self.cogEditorRight)
        self.bodyLayout = wx.BoxSizer(wx.VERTICAL)
        bodyTypeLabel = wx.StaticText(self.cogEditorTabBody, label = "Body Type")
        bodyTypeLabel.SetFont(self.uiFontNormal)
        self.bodyTypeSelection = wx.ComboBox(self.cogEditorTabBody, choices = ["A", "B", "C"])
        self.bodyTypeSelection.Bind(wx.EVT_COMBOBOX, self.setBody)

        bodyScaleLabel = wx.StaticText(self.cogEditorTabBody, label = "Scale")
        bodyScaleLabel.SetFont(self.uiFontNormal)
        self.bodyScale = FloatSpin(self.cogEditorTabBody, size = self.FromDIP(wx.Size((400, 25))), min_val = 0.1, max_val = 4.0, increment = 0.01, value = 1.0, digits = 8)
        self.bodyScale.Bind(wx.EVT_SPINCTRL, self.setBodySize)

        heightLabel = wx.StaticText(self.cogEditorTabBody, label = 'Nametag Height')
        heightLabel.SetFont(self.uiFontNormal)
        self.heightSpin = FloatSpin(self.cogEditorTabBody, size = self.FromDIP(wx.Size((400, 25))), min_val = 0.1, max_val = 15, increment = 0.1, value = 9.0, digits = 8)
        self.heightSpin.Bind(wx.EVT_SPINCTRL, self.setHeight)

        torsoTexLabel = wx.StaticText(self.cogEditorTabBody, label = "Torso Texture")
        torsoTexLabel.SetFont(self.uiFontNormal)
        self.torsoTex = wx.FilePickerCtrl(self.cogEditorTabBody,
                                          size = self.FromDIP(wx.Size((400, 25))),
                                          path = self.cogPreview.torsoTex,
                                          wildcard = "Realms Texture Files (*.png)|*.png",
                                          message = "Select a Torso Texture")
        self.torsoTex.SetInitialDirectory(abspath(DPDKGlobal.DKBase.gameResourcesPath))
        self.torsoTex.Bind(wx.EVT_FILEPICKER_CHANGED, self.setTorsoTex)

        armTexLabel = wx.StaticText(self.cogEditorTabBody, label = "Arm Texture")
        armTexLabel.SetFont(self.uiFontNormal)
        self.armTex = wx.FilePickerCtrl(self.cogEditorTabBody,
                                        size = self.FromDIP(wx.Size((400, 25))),
                                        path = self.cogPreview.armTex,
                                        wildcard = "Realms Texture Files (*.png)|*.png",
                                        message = "Select an Arm Texture")
        self.armTex.SetInitialDirectory(abspath(DPDKGlobal.DKBase.gameResourcesPath))
        self.armTex.Bind(wx.EVT_FILEPICKER_CHANGED, self.setArmTex)

        legTexLabel = wx.StaticText(self.cogEditorTabBody, label = "Leg Texture")
        legTexLabel.SetFont(self.uiFontNormal)
        self.legTex = wx.FilePickerCtrl(self.cogEditorTabBody,
                                        size = self.FromDIP(wx.Size((400, 25))),
                                        path = self.cogPreview.legTex,
                                        wildcard = "Realms Texture Files (*.png)|*.png",
                                        message = "Select a Leg Texture")
        self.legTex.SetInitialDirectory(abspath(DPDKGlobal.DKBase.gameResourcesPath))
        self.legTex.Bind(wx.EVT_FILEPICKER_CHANGED, self.setLegTex)

        handColorLabel = wx.StaticText(self.cogEditorTabBody, label = 'Hands Color')
        handColorLabel.SetFont(self.uiFontNormal)
        self.handColorButton = wx.Button(self.cogEditorTabBody, label = 'Choose Color')
        self.handColorCurrent = wx.StaticText(self.cogEditorTabBody, label = '(255, 255, 255, 255)')
        self.handColorPicker = CubeColourDialog(self.cogEditorTabBody)
        self.handColorButton.Bind(wx.EVT_BUTTON, self.chooseHandColor)

        bodyColorLabel = wx.StaticText(self.cogEditorTabBody, label = 'Body Color Scale')
        bodyColorLabel.SetFont(self.uiFontNormal)
        self.bodyColorButton = wx.Button(self.cogEditorTabBody, label = 'Choose Color')
        self.bodyColorCurrent = wx.StaticText(self.cogEditorTabBody, label = '(255, 255, 255, 255)')
        self.bodyColorPicker = CubeColourDialog(self.cogEditorTabBody)
        self.bodyColorButton.Bind(wx.EVT_BUTTON, self.chooseBodyColor)

        previewRotationLabel = wx.StaticText(self.cogEditorTabBody, label = 'Preview Rotation')
        previewRotationLabel.SetFont(self.uiFontNormal)
        self.previewRotationSlider = wx.Slider(self.cogEditorTabBody,
                                               minValue = -180,
                                               maxValue = 180,
                                               size = self.FromDIP(wx.Size(200, 20)))
        self.previewRotationSlider.Bind(wx.EVT_SLIDER, self.__rotatePreview)

        self.bodyLayout.AddMany(
            (bodyTypeLabel,
             self.bodyTypeSelection,
             bodyScaleLabel,
             self.bodyScale,
             heightLabel,
             self.heightSpin,
             torsoTexLabel,
             self.torsoTex,
             armTexLabel,
             self.armTex,
             legTexLabel,
             self.legTex,
             handColorLabel,
             self.handColorButton,
             self.handColorCurrent,
             bodyColorLabel,
             self.bodyColorButton,
             self.bodyColorCurrent,
             previewRotationLabel,
             self.previewRotationSlider
             ))

        self.cogEditorTabBody.SetSizer(self.bodyLayout)
        # == HEAD TAB ==
        self.cogEditorTabHead = wx.Panel(self.cogEditorRight, size = self.FromDIP(wx.Size(400, 900)))
        headLay = wx.BoxSizer(wx.VERTICAL)

        self.bottomBar = wx.Panel(self.cogEditorTabHead)
        bottomBarLayout = wx.BoxSizer(wx.HORIZONTAL)
        applyButton = wx.Button(self.bottomBar, label = 'Apply')
        applyButton.Bind(wx.EVT_BUTTON, self.updateHeads)
        newButton = wx.Button(self.bottomBar, label = 'Add Head Part')
        newButton.Bind(wx.EVT_BUTTON, self.newHead)
        bottomBarLayout.AddMany((applyButton, newButton))
        self.bottomBar.SetSizer(bottomBarLayout)

        self.cogHeadList = ScrolledPanel(self.cogEditorTabHead, size = self.FromDIP(wx.Size(420, 900)))

        self.headLayout = wx.BoxSizer(wx.VERTICAL)

        self.cogHeadList.SetSizer(self.headLayout)
        self.cogHeadList.SetupScrolling()

        headLay.AddMany((
            self.bottomBar,
            self.cogHeadList))
        self.cogEditorTabHead.SetSizer(headLay)

        # == Info TAB ==
        self.cogEditorTabInfo = wx.Panel(self.cogEditorRight)
        infoLayout = wx.BoxSizer(wx.VERTICAL)

        self.nameLabel = wx.StaticText(self.cogEditorTabInfo, label = f'Name: "{DataPackManager.getLocalizedText(self.cogPreview.name)}"')
        self.nameInput = wx.TextCtrl(self.cogEditorTabInfo, size = self.FromDIP(wx.Size(400, 25)))
        self.nameInput.Bind(wx.EVT_TEXT, self.__updateNames)

        self.nameSLabel = wx.StaticText(self.cogEditorTabInfo, label = f'Name (Singular Form): "{DataPackManager.getLocalizedText(self.cogPreview.nameS)}"')
        self.nameSInput = wx.TextCtrl(self.cogEditorTabInfo, size = self.FromDIP(wx.Size(400, 25)))
        self.nameSInput.Bind(wx.EVT_TEXT, self.__updateNames)

        self.namePLabel = wx.StaticText(self.cogEditorTabInfo, label = f'Name (Plural Form): "{DataPackManager.getLocalizedText(self.cogPreview.nameP)}"')
        self.namePInput = wx.TextCtrl(self.cogEditorTabInfo, size = self.FromDIP(wx.Size(400, 25)))
        self.namePInput.Bind(wx.EVT_TEXT, self.__updateNames)

        self.exitCogButton = wx.Button(
            self.cogEditorTabInfo, label = 'Back to Cog list'
        )
        self.exitCogButton.Bind(wx.EVT_BUTTON, self.unloadCog)

        infoLayout.AddMany((
            self.nameLabel,
            self.nameInput,
            self.nameSLabel,
            self.nameSInput,
            self.namePLabel,
            self.namePInput,
            self.exitCogButton
        ))
        self.cogEditorTabInfo.SetSizer(infoLayout)

        # == Cog List Tab ==
        self.cogEditorTabList = wx.Panel(self.cogEditorRight)
        listLayout = wx.BoxSizer(wx.VERTICAL)
        self.cogEditorTabList.SetSizer(listLayout)
        noCogs = wx.StaticText(self.cogEditorTabList, label = 'There are no Cog appearances in your data pack. Create a new one below.')
        listLayout.Add(noCogs)

        tempLoad = wx.Button(self.cogEditorTabList, label = "New Override")
        tempLoad.Bind(wx.EVT_BUTTON, self.chooseNewOverride)
        listLayout.Add(tempLoad)

        self.cogOverridesList = ScrolledPanel(self.cogEditorTabList, size = self.FromDIP(wx.Size(300, 500)))

        self.cogOverridesLayout = wx.BoxSizer(wx.VERTICAL)

        self.cogOverridesList.SetSizer(self.cogOverridesLayout)
        self.cogOverridesList.SetupScrolling()

        listLayout.Add(self.cogOverridesList)

        self.cogEditorTabBody.Hide()
        self.cogEditorTabHead.Hide()
        self.cogEditorTabInfo.Hide()
        self.cogEditorTabList.Hide()

        # add them all to tabs
        self.cogEditorRight.AddPage(self.cogEditorTabList, "Cogs")

        # self.loadCog()

    def updateOverrides(self):
        for cog in self.cogOverrideItems:
            cog.Destroy()
        self.cogOverrideItems = []

        self.cogOverridesLayout.Clear()

        if not os.path.exists(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/'):
            os.mkdir(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/')

        if not os.path.exists(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/'):
            os.mkdir(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/')

        for file in os.listdir(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/'):
            if os.path.exists(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/{file}'):
                self.cogOverrideItems.append(CogOverrideItem(
                    overrideName = file,
                    parent = self.cogOverridesList,
                    sdkInterface = self
                ))

        self.refreshOverrides()

    def refreshOverrides(self):
        self.cogOverridesLayout.Clear()
        for cog in self.cogOverrideItems:
            self.cogOverridesLayout.Add(cog)
        self.cogOverridesList.SetupScrolling()

    def __rotatePreview(self, e: CommandEvent):
        self.cogPreview.setH(180 + e.GetInt())

    def __setHandColor(self, r: float, g: float, b: float, a: float):
        self.handColorCurrent.SetLabel(f'({r}, {g}, {b}, {a})')
        self.cogPreview.setHandColor(r, g, b, a)

    def chooseHandColor(self, _):
        if self.bodyColorPicker.ShowModal() == wx.ID_OK:
            colorData = self.bodyColorPicker.GetColourData()
            color = colorData.GetColour()
            r, g, b, a = color.Red() / 255., color.Green() / 255., color.Blue() / 255., color.Alpha() / 255.
            self.__setHandColor(r, g, b, a)

    def __setBodyColor(self, r: float, g: float, b: float, a: float):
        self.bodyColorCurrent.SetLabel(f'({r}, {g}, {b}, {a})')
        self.cogPreview.changeColor(r, g, b, a)

    def chooseBodyColor(self, _):
        if self.bodyColorPicker.ShowModal() == wx.ID_OK:
            colorData = self.bodyColorPicker.GetColourData()
            color = colorData.GetColour()
            r, g, b, a = color.Red() / 255., color.Green() / 255., color.Blue() / 255., color.Alpha() / 255.
            self.__setBodyColor(r, g, b, a)

    def updateHeads(self, _):
        self.cogPreview.clearHeads()
        for headItem in self.headItems:
            self.cogPreview.addHead(headItem.get())

    def refreshHeadList(self):
        self.headLayout.Clear()
        for head in self.headItems:
            self.headLayout.Add(head)
        self.cogHeadList.SetupScrolling()

    def newHead(self, _):
        _head = HeadItem(self.cogHeadList, self)
        self.headItems.append(_head)
        self.headLayout.Add(_head)

        self.cogHeadList.SetupScrolling()

    def addHead(self, js: Dict):
        _head = HeadItem(self.cogHeadList, self)
        _head.setInitial(
            js.get('path'),
            js.get('node', ''),
            js.get('texture', ''),
            js.get('position', (0, 0, 0)),
            js.get('rotation', (0, 0, 0)),
            js.get('scale', (1, 1, 1)),
            js.get('color_scale', (1, 1, 1, 1)),
            js.get('remove_nodes', [])
        )

        self.headItems.append(_head)
        self.headLayout.Add(_head)
        self.cogHeadList.SetupScrolling()

    def setBody(self, _):
        self.cogPreview.setBody(self.bodyTypeSelection.GetSelection())

    def setBodySize(self, _):
        self.cogPreview.setSize(self.bodyScale.GetValue())

    def setHeight(self, _):
        self.cogPreview.setHeight(self.heightSpin.GetValue())

    def setTorsoTex(self, e: wx.FileDirPickerEvent):
        if not e.GetPath():
            phaseLocation = ''
        else:
            phaseLocation = Path(relpath(e.GetPath(), DPDKGlobal.DKBase.gameResourcesPath)).as_posix()
        if not phaseLocation.startswith('.'):
            self.torsoTex.SetPath(phaseLocation)
            self.cogPreview.setTorsoTexture(phaseLocation)
        else:
            self.cogPreview.setTorsoTexture(e.GetPath())

    def setArmTex(self, e: wx.FileDirPickerEvent):
        if not e.GetPath():
            phaseLocation = ''
        else:
            phaseLocation = Path(relpath(e.GetPath(), DPDKGlobal.DKBase.gameResourcesPath)).as_posix()
        if not phaseLocation.startswith('.'):
            self.armTex.SetPath(phaseLocation)
            self.cogPreview.setArmTexture(phaseLocation)
        else:
            self.cogPreview.setArmTexture(e.GetPath())

    def setLegTex(self, e: wx.FileDirPickerEvent):
        if not e.GetPath():
            phaseLocation = ''
        else:
            phaseLocation = Path(relpath(self.legTex.GetPath(), DPDKGlobal.DKBase.gameResourcesPath)).as_posix()
        if not phaseLocation.startswith('.'):
            self.legTex.SetPath(phaseLocation)
            self.cogPreview.setLegTexture(phaseLocation)
        else:
            self.cogPreview.setLegTexture(e.GetPath())

    def loadCog(self, _):
        self.cogPreview.show()
        self.cogEditorRight.RemovePage(0)
        self.cogEditorRight.AddPage(self.cogEditorTabBody, "Body")
        self.cogEditorRight.AddPage(self.cogEditorTabHead, "Heads")
        self.cogEditorRight.AddPage(self.cogEditorTabInfo, "Info")

    def unloadCog(self, _ = None):
        self.cogPreview.hide()
        self.cogPreview.activeCogFile = None
        self.cogEditorRight.RemovePage(0)
        self.cogEditorRight.RemovePage(0)
        self.cogEditorRight.RemovePage(0)
        self.cogEditorRight.AddPage(self.cogEditorTabList, "Cogs")
        self.updateOverrides()

    def __updateNames(self, _):
        self.cogPreview.setName(self.nameInput.GetValue())
        self.cogPreview.setNameSingular(self.nameSInput.GetValue())
        self.cogPreview.setNamePlural(self.namePInput.GetValue())

        self.nameLabel.SetLabel(f'Name: "{DataPackManager.getLocalizedText(self.cogPreview.name)}"')
        self.nameSLabel.SetLabel(f'Name (Singular Form): "{DataPackManager.getLocalizedText(self.cogPreview.nameS)}"')
        self.namePLabel.SetLabel(f'Name (Plural Form): "{DataPackManager.getLocalizedText(self.cogPreview.nameP)}"')

    def chooseNewOverride(self, _):
        cogs = []
        filePaths = []
        for defaultCog in glob.glob(os.path.join(DPDKGlobal.DKBase.gameResourcesPath, 'phase_3/data/cogs/appearance/*.json')):
            with open(defaultCog, 'r') as cog:
                js = json.load(cog)
                name = DataPackManager.getLocalizedText(js.get('name', 'improperly formatted appearance file!'))
                cogs.append(f'{os.path.basename(defaultCog)} | {name}')
                filePaths.append(abspath(defaultCog))
        dialog: wx.SingleChoiceDialog
        with wx.SingleChoiceDialog(parent = self, caption = 'Choose a Cog', choices = cogs, message = 'Choose a default Cog to override') as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                path = filePaths[dialog.GetSelection()]
                filename = os.path.basename(path)
                shutil.copy(path, f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/{filename}')
                self.loadCogFile(f'sdk/packs/{DPDKGlobal.DKBase.activePack}/cogs/appearance/{filename}')

    def loadCogFile(self, filePath: str):
        self.cogPreview.activeCogFile = None
        self.cogPreview.clearHeads()
        self.headLayout.Clear()
        for head in self.headItems:
            head.Destroy()
        self.headItems = []
        with open(filePath, 'r') as cog:
            js = json.load(cog)
            for head in js['head_models']:
                self.addHead(head)

            self.cogPreview.setSkeleton(js.get('is_skeleton', False))

            self.bodyTypeSelection.Select(js.get('body_type', 0))
            self.setBody(None)
            self.bodyScale.SetValue(js.get('scale', 1))
            self.setBodySize(None)
            self.heightSpin.SetValue(js.get('height', 9))
            self.setHeight(None)

            if not js.get('is_skeleton', False):
                _torsoEvent = wx.FileDirPickerEvent()
                _torsoEvent.SetPath(js.get('torso_texture', ''))
                self.torsoTex.SetPath(js.get('torso_texture', ''))
                self.setTorsoTex(_torsoEvent)

                _armEvent = wx.FileDirPickerEvent()
                _armEvent.SetPath(js.get('arm_texture', ''))
                self.armTex.SetPath(js.get('arm_texture', ''))
                self.setArmTex(_armEvent)

                _legEvent = wx.FileDirPickerEvent()
                _legEvent.SetPath(js.get('leg_texture', ''))
                self.legTex.SetPath(js.get('leg_texture', ''))
                self.setLegTex(_legEvent)

                self.__setHandColor(*js.get('hand_color', (1, 1, 1, 1)))
            self.__setBodyColor(*js.get('color_scale', (1, 1, 1, 1)))

            self.nameInput.SetValue(js.get('name'))
            self.nameSInput.SetValue(js.get('name_singular'))
            self.namePInput.SetValue(js.get('name_plural'))
            self.__updateNames(None)

            self.cogPreview.setQuoteSets(js.get('quote_sets', []))

        self.loadCog(None)
        self.updateHeads(None)
        self.cogPreview.activeCogFile = filePath

    def setupSettingsPage(self):
        # === Settings Page ===
        self.settingsPage = wx.Panel(self.tabFrame)
        self.settingsPage.Hide()
        self.settingsLayout = wx.BoxSizer(wx.VERTICAL)

        userSettingsLabel = wx.StaticText(self.settingsPage, label = "User Settings")
        userSettingsLabel.SetFont(self.uiFontLarge)
        settingGameInstallLabel = wx.StaticText(self.settingsPage, label = "Toontown Realms Installation Directory")
        settingGameInstallLabel.SetFont(self.uiFontNormal)
        self.settingsGameInstall = wx.FilePickerCtrl(
            self.settingsPage, size = self.FromDIP(wx.Size(400, 20)),
            path = DPDKGlobal.DKBase.settings.get('realms_client_directory', ''),
            message = "TT Realms Installation Directory")
        # add everything to layout
        self.settingsLayout.Add(userSettingsLabel)
        self.settingsLayout.Add(settingGameInstallLabel)
        self.settingsLayout.Add(self.settingsGameInstall)
        self.settingsPage.SetSizer(self.settingsLayout)

    def initialize(self):
        """Initializes the viewports and editor."""
        self.Update()
        ViewportManager.updateAll()
        self.wxStep()
        ViewportManager.initializeAll()
        self.viewport.camLens.setFov(30, 30)

        # to make persp view as default
        # sdelf.perspViewMenuItem.Toggle()

        base.win = base.winList[0]
        base.winList[0].setActive(1)

        # initializing direct

        base.direct = None
        # base.closeWindow(base.win)

    def wxStep(self, task = None):
        """A step in the WX event loop. You can either call this yourself or use as task."""
        while self.evtLoop.Pending():
            self.evtLoop.Dispatch()
        self.evtLoop.ProcessIdle()
        if task is not None:
            return task.cont

    def appInit(self):
        """Overridden from WxAppShell.py."""
        # Create a new event loop (to overide default wxEventLoop)
        self.evtLoop = wx.GUIEventLoop()
        self.oldLoop = wx.GUIEventLoop.GetActive()
        wx.GUIEventLoop.SetActive(self.evtLoop)
        taskMgr.add(self.wxStep, "evtLoopTask")

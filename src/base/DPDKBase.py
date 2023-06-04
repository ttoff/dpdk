from __future__ import annotations

import aiohttp
import asyncio
import glob
import os
import shutil
import sys
import wx
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Multifile, Filename, loadPrcFile, loadPrcFileData, TextProperties, TextPropertiesManager
from pathlib import PurePosixPath
from typing import Dict
from wx.adv import SplashScreen, SPLASH_CENTER_ON_SCREEN

from src.base import DPDKGlobal
from src.ott.Settings import Settings
from src.window.SDKInterface import WxPandaShell


class DPDKBase(WxPandaShell):
    notify = directNotify.newCategory("Data Pack Development Kit")
    notify.setInfo(True)

    # noinspection PyMissingConstructor
    def __init__(self):
        loadPrcFile('sdk.prc')
        base = ShowBase(False, windowType = 'none')
        self.sb = base
        # a much simpler way to hold localizer keys and strings
        self.localizer: Dict[str, str] = {}
        self.gameResourcesPath: str = 'sdk/temp/realms_resources'
        self.activePack: str | None = None
        self.settings = Settings('settings.toml')
        self.wxApp = wx.App(redirect = False)
        self.wxApp.SetAppName("Toontown Realms Data Pack Development Kit")
        img = wx.Bitmap('sdk/assets/ttsdk_i_splash.png', wx.BITMAP_TYPE_PNG)
        self.splash = wx.adv.SplashScreen(img, SPLASH_CENTER_ON_SCREEN, 99999, None)

        if 'realms_client_directory' not in self.settings:
            if os.path.exists(os.path.expandvars("%localappdata%\\Toontown Realms\\")):
                gamePath = os.path.expandvars("%localappdata%\\Toontown Realms\\")
            else:
                clientInstallDir = wx.DirDialog(None, "Select your Toontown Realms Installation Directory", defaultPath = os.path.expandvars("%localappdata%\\"))
                if clientInstallDir.ShowModal() == wx.ID_OK:
                    gamePath = clientInstallDir.GetPath()
                else:
                    sys.exit()
            self.settings['realms_client_directory'] = gamePath
        if not self.settings.get('dont_update_temp_files', False) or not self.settings.get('use_dev_resources', False):
            self.extractGameClient()

        if self.settings.get('use_dev_resources', False):
            if self.settings.get('dev_directory', None) is None:
                self.notify.error('You have use_dev_resources enabled, but did not specify a dev_directory.')
            self.gameResourcesPath = f'{self.settings.get("dev_directory")}\\resources\\'
            loadPrcFileData('settings: dev resources', f'model-path {self.gameResourcesPath}')

            self.fetchLocalizerStringsFromDev()
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.fetchLocalizerStrings())

        self.setupTextProperties()
        self.splash.Close()

    def quit(self, event = None):
        self.notify.info('Exiting SDK... Killing window...')
        self.Hide()
        if not self.settings.get('keep_temp_files', False) or not self.settings.get('use_dev_resources', False):
            self.notify.info('Exiting SDK... Cleaning up temp files...')
            tempDataPath: str = 'sdk/temp/realms_resources'
            if not os.path.exists(tempDataPath):
                os.makedirs('sdk/temp/realms_resources')
            else:
                for file in os.scandir(tempDataPath):
                    if os.path.isfile(file):
                        os.unlink(file)
                    elif os.path.isdir(file):
                        shutil.rmtree(file)
        self.notify.info('Exiting SDK... Done.')

        super().quit(event)

    def runShell(self):
        self.notify.info('Setup complete, creating window...')
        WxPandaShell.__init__(self)

    def extractGameClient(self):
        tempDataPath: str = 'sdk/temp/realms_resources'
        if not os.path.exists(tempDataPath):
            os.makedirs('sdk/temp/realms_resources')
        else:
            for file in os.scandir(tempDataPath):
                if os.path.isfile(file):
                    os.unlink(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)

        path = self.settings.get('realms_client_directory')
        for multifile in (glob.glob(f'{path}resources\\default\\ttrm_mdl_*.pak')
                          + glob.glob(f'{path}resources\\default\\ttrm_tex_*.pak')
                          + glob.glob(f'{path}resources\\default\\ttrm_dat_*.pak')):
            self.notify.info(f'Extracting {multifile}')
            mf: Multifile = Multifile()
            mf.openRead(Filename(PurePosixPath(multifile)))
            for subfile in range(mf.getNumSubfiles()):
                subfileName = mf.getSubfileName(subfile)
                mf.extractSubfile(subfile, f'{tempDataPath}/{subfileName}')

    async def fetchLocalizerStrings(self):
        self.notify.info('Fetching Localizer Strings...')
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://raw.githubusercontent.com/ttoff/modding-docs/master/localizer/otplocalizer.txt') as ttlResp:
                    ttlLines = await ttlResp.text()
                    with open('sdk/temp/otplocalizer.txt', 'w') as ttl:
                        ttl.write(ttlLines)
            except:
                wx.MessageBox('There was an error fetching OTPLocalizer strings. '
                              'This is likely an issue with your connection. '
                              'Localizer strings may not display correctly, '
                              'but this won\'t have any negative affect in-game.',
                              'error!!!!!!!!!!!!!!!!!!!!!!!')

            try:
                async with session.get('https://raw.githubusercontent.com/ttoff/modding-docs/master/localizer/ttlocalizer.txt') as ttlResp:
                    ttlLines = await ttlResp.text()
                    with open('sdk/temp/ttlocalizer.txt', 'w') as ttl:
                        ttl.write(ttlLines)
            except:
                wx.MessageBox('There was an error fetching TTLocalizer strings. '
                              'This is likely an issue with your connection. '
                              'Localizer strings may not display correctly, '
                              'but this won\'t have any negative affect in-game.',
                              'error!!!!!!!!!!!!!!!!!!!!!!!')

        with open('sdk/temp/otplocalizer.txt', 'r') as otpLocalizer:
            for line in otpLocalizer.readlines():
                _line = line.split(' = ')
                if len(_line) == 2:
                    key, value = _line[0], _line[1][1:-2]
                    self.localizer[key] = value

        with open('sdk/temp/ttlocalizer.txt', 'r') as ttLocalizer:
            for line in ttLocalizer.readlines():
                _line = line.split(' = ')
                if len(_line) == 2:
                    key, value = _line[0][1:], _line[1][1:-2]
                    self.localizer[key] = value

    def fetchLocalizerStringsFromDev(self):
        self.notify.info('Importing localization strings from dev')
        sys.path.append(self.settings.get('dev_directory'))
        from toontown.toonbase import TTLocalizerEnglish

        for key, val in TTLocalizerEnglish.__dict__.items():
            self.localizer['#' + key] = val

        from otp.otpbase import OTPLocalizerEnglish
        for key, val in OTPLocalizerEnglish.__dict__.items():
            self.localizer['#' + key] = val

    @staticmethod
    def setupTextProperties():
        tpm: TextPropertiesManager = TextPropertiesManager.getGlobalPtr()
        candidateActive = TextProperties()
        candidateActive.setTextColor(0, 0, 1, 1)
        tpm.setProperties('candidate_active', candidateActive)

        candidateInactive = TextProperties()
        candidateInactive.setTextColor(0.3, 0.3, 0.7, 1)
        tpm.setProperties('candidate_inactive', candidateInactive)

        white = TextProperties()
        white.setTextColor(1.0, 1.0, 1.0, 1.0)
        tpm.setProperties('white', white)

        whiteComedy = TextProperties()
        whiteComedy.setTextColor(1.0, 1.0, 1.0, 1.0)
        whiteComedy.setShadowColor(0.0, 0.0, 0.0, 1.0)
        whiteComedy.setFont(loader.loadFont('phase_3/fonts/Comedy.ttf'))

        tpm.setProperties('white_comedy', whiteComedy)
        WLDisplay = TextProperties()
        WLDisplay.setSlant(0.3)
        tpm.setProperties('WLDisplay', WLDisplay)

        WLEnter = TextProperties()
        WLEnter.setTextColor(1.0, 0.0, 0.0, 1)
        tpm.setProperties('WLEnter', WLEnter)

        WLMagicWord = TextProperties()
        WLMagicWord.setTextColor(0.6, 0.0, 0.6, 1)
        tpm.setProperties('WLMagicWord', WLMagicWord)

        WLMagicWordArg = TextProperties()
        WLMagicWordArg.setTextColor(0.8, 0.4, 0.6, 1)
        tpm.setProperties('WLMagicWordArg', WLMagicWordArg)

        WLMagicWordArgDesc = TextProperties()
        WLMagicWordArgDesc.setTextScale(0.5)
        WLMagicWordArgDesc.setGlyphShift(-.4)
        tpm.setProperties('WLMagicWordArgDesc', WLMagicWordArgDesc)

        del tpm


if __name__ == '__main__':
    DPDKGlobal.DKBase = DPDKBase()
    DPDKGlobal.DKBase.runShell()
    DPDKGlobal.DKBase.sb.run()

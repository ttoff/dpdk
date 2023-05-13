# = Distributed DataPackManager - Client Side =
# Created by drewc on 4/26/2023 11:08 PM
# 5/9/23 - altered version for SDK removing in-game only features
from typing import List, Dict, Optional

from direct.directnotify import DirectNotifyGlobal
from panda3d.core import NodePath, Texture

from src.base import DPDKGlobal


class DataPackManager:
    notify = DirectNotifyGlobal.directNotify.newCategory('DataPackManager')
    notify.setDebug(True)

    @staticmethod
    def getLocalizedText(string: str) -> str:
        """
        Checks if we should are trying to use localized text (starts with #)
        then gets the string from the localizer, otherwise just return the string
        :param string: Raw String
        :return: Localized String
        """
        return DPDKGlobal.DKBase.localizer.get(string, string)

    @staticmethod
    def getModelNode(modelPath: str, nodePath: Optional[str] = None) -> NodePath:
        _model = loader.loadModel(modelPath, okMissing = True)
        if not _model:
            DataPackManager.notify.warning(f'Unable to find model {modelPath}')
            _model = loader.loadModel('phase_3.5/models/props/cube')
        if nodePath is not None:
            if _model.find(f'**/{nodePath}').isEmpty():
                DataPackManager.notify.warning(f'Unable to find node {nodePath} from {_model}')
                return _model
            _np: NodePath = _model.find(f'**/{nodePath}')
            _newNode = NodePath(_np)
            _model.removeNode()
            return _newNode
        return _model

    @staticmethod
    async def getModelNodeAsync(modelPath: str, nodePath: Optional[str] = None) -> NodePath:
        _model = await loader.loadModel(modelPath, okMissing = True, blocking = False)
        if not _model:
            DataPackManager.notify.warning(f'Unable to find model {modelPath}')
            _model = await loader.loadModel('phase_3.5/models/props/cube', blocking = False)
        if nodePath is not None:
            if _model.find(f'**/{nodePath}').isEmpty():
                DataPackManager.notify.warning(f'Unable to find node {nodePath} from {_model}')
                return _model
            _np: NodePath = _model.find(f'**/{nodePath}')
            _newNode = NodePath(_np)
            _model.removeNode()
            return _newNode
        return _model

    @staticmethod
    def getTexture(texturePath: str) -> Texture:
        _texture = loader.loadTexture(texturePath, okMissing = True)
        if not _texture:
            DataPackManager.notify.warning(f'Unable to find texture {texturePath}')
            _texture = loader.loadTexture('phase_3/maps/ttrm_t_gen_textureNotFound.png')
            _texture.setMagfilter(Texture.FTNearest)
        return _texture

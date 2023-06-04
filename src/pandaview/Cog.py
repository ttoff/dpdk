from __future__ import annotations

import json

from typing import List, Dict

from direct.actor.Actor import Actor
from panda3d.core import PartBundle, Texture, NodePath, VBase4, TransparencyAttrib, TextNode, BillboardEffect, Vec3

from src.base import DPDKGlobal
from src.base.ToontownTypes import TCogHead
from src.datapack.DataPackManager import DataPackManager

COG_MODELS = (
    'phase_3.5/models/char/suitA-mod.bam',
    'phase_3.5/models/char/suitB-mod.bam',
    'phase_3.5/models/char/suitC-mod.bam'
)
SKELECOG_MODELS = (
    'phase_5/models/char/cogA_robot-zero.bam',
    'phase_5/models/char/cogB_robot-zero.bam',
    'phase_5/models/char/cogC_robot-zero.bam'
)
IDLE_ANIMS = (
    'phase_4/models/char/suitA-neutral.bam',
    'phase_4/models/char/suitB-neutral.bam',
    'phase_3.5/models/char/suitC-neutral.bam'
)


class Cog(Actor):

    def __init__(self):
        super().__init__(COG_MODELS[0], {'neutral': IDLE_ANIMS[0]})

        self.activeCogFile: str | None = None

        self.loop('neutral')
        self.setTransparency(TransparencyAttrib.MDual)

        self.setBlend(frameBlend = True, blendType = PartBundle.BTComponentwiseQuat)

        self.bodyType: int = 0
        self.torsoTex: str = 'phase_3.5/maps/c_blazer.png'
        self.armTex: str = 'phase_3.5/maps/c_sleeve.png'
        self.legTex: str = 'phase_3.5/maps/c_leg.png'
        self.scale = 1
        self.height = 9

        self.colorScale: VBase4 = VBase4(1, 1, 1, 1)
        self.handColor: VBase4 = VBase4(1, 1, 1, 1)

        self.heads: List[TCogHead] = []

        self.headParts: List[NodePath] = []

        self.name: str = ''
        self.nameS: str = ''
        self.nameP: str = ''

        self.isSkeleton: bool = False
        self.isVirtual: bool = False
        self.quoteSets: List[str] = []
        self.createNametag()

    def createNametag(self):
        self.nametagContainer: NodePath = render.attachNewNode('nametag')
        billboardEffect = BillboardEffect.make(Vec3(0, 0, 1), True, True, 3, base.cam, Vec3(0, 0, 0))
        self.nametagContainer.setEffect(billboardEffect)
        self.nametagContainer.setScale(.3)
        self.nametagPanel: NodePath = loader.loadModel('phase_3/models/props/panel')
        self.nametagPanel.reparentTo(self.nametagContainer)
        self.nametagPanel.setColor(VBase4(0.8, 0.8, 0.8, 0.5))
        self.nametagPanel.setColorScaleOff()
        self.nametagText = TextNode('nametagText')
        self.nametagText.setFont(loader.loadFont('phase_3/fonts/vtRemingtonPortable.ttf'))
        self.nametagText.setTextColor(VBase4(0, 0, 0, 1))
        self.nametagText.setWordwrap(12)
        self.nametagText.setAlign(TextNode.ACenter)
        tnp: NodePath = self.nametagContainer.attachNewNode(self.nametagText, 1)
        tnp.setTransparency(1)
        tnp.setY(-0.05)
        tnp.setDepthOffset(5)
        self.adjustNametag()

    def adjustNametag(self):
        self.nametagText.setText(f'{DataPackManager.getLocalizedText(self.name)}\nDeptBot\nLevel 1')
        # position & resize the panel
        x = (self.nametagText.getLeft() + self.nametagText.getRight()) / 2.0
        z = (self.nametagText.getTop() + self.nametagText.getBottom()) / 2.0
        self.nametagPanel.setPos(x, 0, z)

        width = self.nametagText.getWidth() + 0.5
        height = self.nametagText.getHeight() + 0.2
        self.nametagPanel.setScale(width, 1, height)

        self.nametagContainer.setZ(self.height + 1)

    def setTorsoTexture(self, path: str):
        self.torsoTex = path
        texture = DataPackManager.getTexture(path)
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        self.find('**/torso').setTexture(texture, 1)
        self.updateCog()

    def setArmTexture(self, path: str):
        self.armTex = path
        texture = DataPackManager.getTexture(path)
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        self.find('**/arms').setTexture(texture, 1)
        self.updateCog()

    def setLegTexture(self, path: str):
        self.legTex = path
        texture = DataPackManager.getTexture(path)
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        self.find('**/legs').setTexture(texture, 1)
        self.updateCog()

    def setBody(self, bType: int):
        self.bodyType = bType
        self.removePart('modelRoot')
        self.loadModel(SKELECOG_MODELS[bType] if self.isSkeleton else COG_MODELS[bType])
        self.loadAnims({'neutral': IDLE_ANIMS[bType]})

        self.loop('neutral')

        if not self.isSkeleton:
            self.setTorsoTexture(self.torsoTex)
            self.setArmTexture(self.armTex)
            self.setLegTexture(self.legTex)
            self.find('**/hands').setColor(self.handColor)
        self.loadHeads()

        self.setColorScale(self.colorScale)
        self.adjustNametag()
        self.updateCog()

    def addHead(self, head: TCogHead):
        self.heads.append(head)
        self.loadHeads()

    def clearHeads(self):
        self.heads = []
        for node in self.headParts:
            node.removeNode()
            del node
        self.headParts = []
        self.updateCog()

    def changeColor(self, r: float, g: float, b: float, a: float):
        self.colorScale = VBase4(r, g, b, a)
        self.setColorScale(self.colorScale)
        self.updateCog()

    def setHandColor(self, r: float, g: float, b: float, a: float):
        self.handColor = VBase4(r, g, b, a)
        self.find('**/hands').setColor(self.handColor)
        self.updateCog()

    def setSize(self, scale: float):
        self.scale = scale
        self.getGeomNode().setScale(self.scale)
        self.updateCog()

    def setHeight(self, height: float):
        self.height = height
        self.adjustNametag()
        self.updateCog()

    def setName(self, name: str):
        self.name = name
        self.adjustNametag()
        self.updateCog()

    def setNameSingular(self, name: str):
        self.nameS = name
        self.updateCog()

    def setNamePlural(self, name: str):
        self.nameP = name
        self.updateCog()

    def setVirtual(self, state: bool = False):
        self.isVirtual = state
        self.updateCog()

    def setSkeleton(self, state: bool = False):
        self.isSkeleton = state
        self.setBody(self.bodyType)
        self.updateCog()

    def loadHeads(self):
        for node in self.headParts:
            node.removeNode()
            del node
        self.headParts = []
        for head in self.heads:
            path, node, texture, pos, hpr, scale, colorScale, removeNodes = head

            if node == '':
                node = None

            _headModel = DataPackManager.getModelNode(path, node)
            if self.bodyType == 0:
                headPart = self.instance(_headModel, 'modelRoot', 'to_head')
            else:
                headPart = self.instance(_headModel, 'modelRoot', 'joint_head')
            if texture != '':
                headTex = DataPackManager.getTexture(texture)
                headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                headPart.setTexture(headTex, 1)

            for node in removeNodes:
                _np = headPart.find(f'**/{node}')
                if not _np.isEmpty():
                    _np.removeNode()

            headPart.setPosHprScale(*pos, *hpr, *scale)
            headPart.setColorScale(colorScale)

            self.headParts.append(headPart)

            _headModel.removeNode()
        self.updateCog()

    def setQuoteSets(self, sets: List[str] | None = None):
        if sets is None:
            sets = []
        self.quoteSets = sets

    def toJson(self) -> Dict:
        jdict = {
            'head_models': [],
            'body_type': self.bodyType,
            'scale': self.scale,
            'height': self.height,
            'torso_texture': self.torsoTex,
            'arm_texture': self.armTex,
            'leg_texture': self.legTex,
            'name': self.name,
            'name_singular': self.nameS,
            'name_plural': self.nameP,
            'hand_color': [*self.handColor],
            'color_scale': [*self.colorScale],
            'is_skeleton': self.isSkeleton,
            'is_virtual': self.isVirtual,
            'quote_sets': self.quoteSets
        }

        for path, node, texture, pos, hpr, scale, colorScale, removeNodes in self.heads:
            jdict['head_models'].append({
                'path': path,
                'node': node,
                'texture': texture,
                'position': [*pos],
                'rotation': [*hpr],
                'scale': [*scale],
                'color_scale': [*colorScale],
                'remove_nodes': removeNodes
            })
        return jdict

    def updateCog(self):
        if not self.activeCogFile:
            return
        DPDKGlobal.DKBase.notify.debug(self.toJson())
        with open(self.activeCogFile, 'w') as file:
            file.write(json.dumps(self.toJson(), indent = 4))

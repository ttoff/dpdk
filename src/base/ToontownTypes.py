"""
Just some aliases for types in TT Realms
"""

from typing import Tuple, List, Dict

# Some places in the game (like networking related stuff) pass colors as a tuple of 4 floats, not a VBase4
TColor = Tuple[float, float, float, float]
TVec3 = Tuple[float, float, float]

# Shirt: (shirtId, shirtColor, sleeveId, sleeveColor)
TShirt = Tuple[int, TColor, int, TColor]
TBottom = Tuple[int, TColor]

TAccessory = Tuple[int, int, int]

# DataPack
TCogHead = Tuple[
    str,  # path
    str,  # node
    str,  # texture
    TVec3,  # pos offset
    TVec3,  # hpr offset
    TVec3,  # scale
    TColor,  # color
    List[str]  # nodes to remove (incase we want to keep all but some nodes in a model)
]
TCogAppearance = Tuple[
    str,  # COG ABBREVIATION
    List[TCogHead],  # COG HEAD MODEL(S)
    int,  # BODY TYPE
    float,  # SCALE
    float,  # HEIGHT
    str,  # TORSO TEX
    str,  # LEG TEX
    str,  # ARM TEX

    str,  # NAME
    str,  # NAME SINGULAR
    str,  # NAME PLURAL
    TColor,  # HAND COLOR
    TColor,  # COLOR SCALE
    bool,  # isSkeleton
    bool  # isVirtual
]
TCogAppearance_D = Tuple[
    List[TCogHead],  # COG HEAD MODEL(S)
    int,  # BODY TYPE
    float,  # SCALE
    float,  # HEIGHT
    str,  # TORSO TEX
    str,  # LEG TEX
    str,  # ARM TEX

    str,  # NAME
    str,  # NAME SINGULAR
    str,  # NAME PLURAL
    TColor,  # HAND COLOR
    TColor  # COLOR SCALE
]


class CogAppearanceIndex:
    HEAD = 0
    BODY_TYPE = 1
    SCALE = 2
    HEIGHT = 3
    TORSO_TEX = 4
    LEG_TEX = 5
    ARM_TEX = 6
    NAME = 7
    NAME_SINGULAR = 8
    NAME_PLURAL = 9
    HAND_COLOR = 10
    COLOR_SCALE = 11
# -*- coding: utf-8-*-
"""
Module : QPanda3D_Translation_Modifiers
Author : Niklas Mevenkamp
Description :
    Contains a dictionary that translates QT keyboard events to panda3d
    keyboard events.
"""
# PyQt imports
from PyQt6.QtCore import Qt

__all__ = ["QPanda3D_Modifier_translation"]

QPanda3D_Modifier_translation = {
    Qt.KeyboardModifier.NoModifier: None,
    Qt.KeyboardModifier.ShiftModifier: "shift",
    Qt.KeyboardModifier.ControlModifier: "control",
    Qt.KeyboardModifier.AltModifier: "alt",
    Qt.KeyboardModifier.MetaModifier: "unknown",
    Qt.KeyboardModifier.KeypadModifier: "unknown",
    Qt.KeyboardModifier.GroupSwitchModifier: "unknown",
}

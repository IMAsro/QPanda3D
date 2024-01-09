# -*- coding: utf-8-*-
"""
Module : QPanda3DWidget
Author : Saifeddine ALOUI
Description :
    This is the QWidget to be inserted in your standard PyQt6 application.
    It takes a Panda3DWorld object at init time.
    You should first create the Panda3DWorld object before creating this widget.
"""
from __future__ import annotations

from ctypes import c_void_p, memmove

import numpy as np
from direct.showbase import MessengerGlobal
from direct.task import TaskManagerGlobal
from PyQt6.QtCore import QSize, QSizeF, Qt, QTimer
from PyQt6.QtGui import (
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QWheelEvent,
)
from PyQt6.QtWidgets import QWidget

from QPanda3D.Panda3DWorld import Panda3DWorld
from QPanda3D.QPanda3D_Buttons_Translation import QPanda3D_Button_translation
from QPanda3D.QPanda3D_Keys_Translation import QPanda3D_Key_translation
from QPanda3D.QPanda3D_Modifiers_Translation import QPanda3D_Modifier_translation

__all__ = ["QPanda3DWidget"]


class QPanda3DSynchronizer(QTimer):
    def __init__(self, qPanda3DWidget: QPanda3DWidget, FPS=60):
        QTimer.__init__(self)
        self.qPanda3DWidget = qPanda3DWidget
        dt = 1000 // FPS
        self.setInterval(dt)
        self.timeout.connect(self.tick)

    def tick(self):
        if self.isActive():
            TaskManagerGlobal.taskMgr.step()
            self.qPanda3DWidget.update()

    def __del__(self):
        self.stop()


def get_panda_key_modifiers(event: QKeyEvent | QWheelEvent | QMouseEvent):
    panda_mods = []
    qt_mods = event.modifiers()
    for qt_mod, panda_mod in QPanda3D_Modifier_translation.items():
        if (qt_mods & qt_mod) == qt_mod:
            panda_mods.append(panda_mod)
    return panda_mods


def get_panda_key_modifiers_prefix(event):
    # join all modifiers (except NoModifier, which is None) with '-'
    mods = [mod for mod in get_panda_key_modifiers(event) if mod is not None]
    prefix = "-".join(mods)

    # Fix the case where the modifier key is pressed alone without other things
    # if not things like control-control would be possible
    if isinstance(event, QMouseEvent):
        key = QPanda3D_Button_translation[event.button()]
    elif isinstance(event, QKeyEvent):
        key = QPanda3D_Key_translation[event.key()]
    elif isinstance(event, QWheelEvent):
        key = "wheel"
    else:
        raise NotImplementedError("Unknown event type")

    if key in mods:
        mods.remove(key)
        prefix = "-".join(mods)

    # if the prefix is not empty, append a '-'
    if prefix == "-":
        prefix = ""
    if prefix:
        prefix += "-"

    return prefix


class QPanda3DWidget(QWidget):
    """
    An interactive panda3D QWidget
    Parent : Parent QT Widget
    FPS : Number of frames per socond to refresh the screen
    debug: Switch printing key events to console on/off
    """

    def __init__(self, panda3DWorld: Panda3DWorld, parent=None, FPS=60, debug=False):
        QWidget.__init__(self, parent)

        # set fixed geometry
        self.panda3DWorld = panda3DWorld
        self.panda3DWorld.set_parent(self)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.painter = QPainter()
        self.out_image = QImage()

        size = self.panda3DWorld.cam.node().get_lens().get_film_size()
        self.initial_film_size = QSizeF(size.x, size.y)
        self.initial_size = self.size()

        self.synchronizer = QPanda3DSynchronizer(self, FPS)
        self.synchronizer.start()

        self.debug = debug

    def mousePressEvent(self, event: QMouseEvent):
        button = event.button()
        try:
            b = f"{get_panda_key_modifiers_prefix(event)}{QPanda3D_Button_translation[button]}"
            if self.debug:
                print(b)
            MessengerGlobal.messenger.send(b, [{"x": event.pos().x(), "y": event.pos().y()}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def mouseMoveEvent(self, event: QMouseEvent):
        # button = event.button() # not used, is it unnecessary
        try:
            b = "mouse-move"
            if self.debug:
                print(b)
            MessengerGlobal.messenger.send(b, [{"x": event.pos().x(), "y": event.pos().y()}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def mouseReleaseEvent(self, event: QMouseEvent):
        button = event.button()
        try:
            b = f"{get_panda_key_modifiers_prefix(event)}{QPanda3D_Button_translation[button]}-up"
            if self.debug:
                print(b)
            MessengerGlobal.messenger.send(b, [{"x": event.pos().x(), "y": event.pos().y()}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def wheelEvent(self, event: QMouseEvent):
        delta = event.angleDelta().y()
        try:
            w = f"{get_panda_key_modifiers_prefix(event)}wheel"
            if self.debug:
                print(f"{w} {delta}")
            MessengerGlobal.messenger.send(w, [{"delta": delta}])
        except Exception as e:
            print("Unimplemented button. Please send an issue on github to fix this problem")
            print(e)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        try:
            k = f"{get_panda_key_modifiers_prefix(event)}{QPanda3D_Key_translation[key]}"
            if self.debug:
                print(k)
            MessengerGlobal.messenger.send(k)
        except Exception as e:
            print("Unimplemented key. Please send an issue on github to fix this problem")
            print(e)

    def keyReleaseEvent(self, event: QKeyEvent):
        key = event.key()
        try:
            k = f"{get_panda_key_modifiers_prefix(event)}{QPanda3D_Key_translation[key]}-up"
            if self.debug:
                print(k)
            MessengerGlobal.messenger.send(k)
        except Exception as e:
            print("Unimplemented key. Please send an issue on github to fix this problem")
            print(e)

    def resizeEvent(self, event: QResizeEvent):
        lens = self.panda3DWorld.cam.node().get_lens()
        lens.set_film_size(self.initial_film_size.width() * event.size().width() / self.initial_size.width(), self.initial_film_size.height() * event.size().height() / self.initial_size.height())
        self.panda3DWorld.buff.setSize(event.size().width(), event.size().height())

    def minimumSizeHint(self):
        return QSize(400, 300)

    # Use the paint event to pull the contents of the panda texture to the widget
    def paintEvent(self, event: QPaintEvent):
        texture = self.panda3DWorld.screenTexture
        if texture.mightHaveRamImage():
            data = texture.getRamImage().getData()
            width, height = texture.getXSize(), texture.getYSize()

            # Create a buffer, transpose and rotate the image data
            buf = np.frombuffer(data, dtype=np.uint8)
            buf = buf.reshape((height, width, 4))  # Reshape considering height and width
            buf_transposed = np.ascontiguousarray(np.rot90(np.transpose(buf, (1, 0, 2))))

            # recreate the QImage if the size changed
            if self.out_image.size() != QSize(height, width):
                self.out_image = QImage(width, height, QImage.Format.Format_ARGB32)

            memmove(c_void_p(self.out_image.bits().__int__()), buf_transposed.ctypes.data, buf_transposed.size)

            self.painter.begin(self)
            self.painter.drawImage(0, 0, self.out_image)
            self.painter.end()
        event.accept()

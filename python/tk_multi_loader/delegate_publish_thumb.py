# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from typing import Callable

from sgtk.platform.qt import QtCore

from .ui.widget_publish_thumb import Ui_PublishThumbWidget
from .delegate_publish import PublishWidget, PublishDelegate


class PublishThumbWidget(PublishWidget):
    """
    Thumbnail style widget which contains an image and some
    text underneath. The widget scales gracefully.
    Used in the main loader view.
    """

    def __init__(self, parent):
        """
        :param parent: QT parent object
        """
        PublishWidget.__init__(self, Ui_PublishThumbWidget, parent)

    def set_text(self, header, body):
        """
        Populate the lines of text in the widget

        :param header: Header text as string
        :param body: Body text as string
        """
        msg = "<b>%s</b><br>%s" % (header, body)
        self.ui.label.setText(msg)

    @staticmethod
    def calculate_size(scale_factor):
        """
        Calculates and returns a suitable size for this widget given a scale factor
        in pixels.

        :returns: Size of the widget
        """
        # the thumbnail proportions are 512x400
        # add another 34px for the height so the text can be rendered.
        return QtCore.QSize(scale_factor, (scale_factor * 0.78125) + 34)


class SgPublishThumbDelegate(PublishDelegate):
    """
    Delegate which 'glues up' the Thumb widget with a QT View.
    """

    def _create_widget(self, parent):
        """
        Widget factory as required by base class. The base class will call this
        when a widget is needed and then pass this widget in to the various callbacks.

        :param parent: Parent object for the widget
        """
        return PublishThumbWidget(parent)

    @property
    def _format_folder_callback(
        self,
    ) -> Callable[[QtCore.QModelIndex, bool], tuple[str, str]]:
        """Get hook callback method for formatting a folder item texts."""
        return self._format_hook.format_thumbnail_folder

    @property
    def _format_publish_callback(
        self,
    ) -> Callable[[QtCore.QModelIndex, bool], tuple[str, str]]:
        """Get hook callback method for formatting a published file item texts."""
        return self._format_hook.format_thumbnail_publish

    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.

        :param style_options: QT style options
        :param model_index: Model item to operate on
        """
        # base the size of each element off the icon size property of the view
        scale_factor = self._view.iconSize().width()
        return PublishThumbWidget.calculate_size(scale_factor)

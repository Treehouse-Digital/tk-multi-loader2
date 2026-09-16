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

from .ui.widget_publish_list import Ui_PublishListWidget
from .delegate_publish import PublishWidget, PublishDelegate


class PublishListWidget(PublishWidget):
    """
    Fixed height thin list item type widget, used for the list mode in the main loader view.
    """

    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        """
        PublishWidget.__init__(self, Ui_PublishListWidget, parent)

    def set_text(self, large_text, small_text):
        """
        Populate the lines of text in the widget

        :param large_text: Header text as string
        :param small_text: smaller text as string
        """
        self.ui.label_1.setText(large_text)
        self.ui.label_2.setText(small_text)

    @staticmethod
    def calculate_size():
        """
        Calculates and returns a suitable size for this widget.

        :returns: Size of the widget
        """
        return QtCore.QSize(200, 56)


class SgPublishListDelegate(PublishDelegate):
    """
    Delegate which 'glues up' the List widget with a QT View.
    """

    def _create_widget(self, parent):
        """
        Widget factory as required by base class. The base class will call this
        when a widget is needed and then pass this widget in to the various callbacks.

        :param parent: Parent object for the widget
        """
        return PublishListWidget(parent)

    @property
    def _format_folder_callback(
        self,
    ) -> Callable[[QtCore.QModelIndex, bool], tuple[str, str]]:
        """Get hook callback method for formatting a folder item texts."""
        return self._format_hook.format_list_folder

    @property
    def _format_publish_callback(
        self,
    ) -> Callable[[QtCore.QModelIndex, bool], tuple[str, str]]:
        """Get hook callback method for formatting a published file item texts."""
        return self._format_hook.format_list_publish

    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.

        :param style_options: QT style options
        :param model_index: Model item to operate on
        """
        return PublishListWidget.calculate_size()

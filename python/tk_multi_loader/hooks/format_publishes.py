# Copyright (c) 2026 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
"""Base hook for formatting publishes in the loader.

This is called by the various delegate classes to format the text used for the
list/thumbnail views.

Having it as a hook allows for customization depending on the context this Loader app is
running in e.g.:

- An asset library project vs a production VFX project
- Different DCCs
- Highlight specific publishes related to current shot/asset

"""

from __future__ import annotations

import datetime

import sgtk
from sgtk.platform.qt import QtCore

__all__ = ("FormatPublishes",)


class FormatPublishes(sgtk.get_hook_baseclass()):
    """Base hook for formatting.

    Uses the exact same code extracted from `tk-multi-loader v1.25.6
    <https://github.com/shotgunsoftware/tk-multi-loader2/blob/v1.25.6/python/tk_multi_loader>`_:

    - ``delegate_publish_list.py``
    - ``delegate_publish_thumb.py``

    Notable attributes exposed to help with calculating and formatting publishes:

    - (class-level) ``shotgun_globals``, imported from
      `tk-framework-shotgunutils.shotgun_globals
      <https://developers.shotgridsoftware.com/tk-framework-shotgunutils/shotgun_globals.html>`_
    - (class-level) ``shotgun_model``, imported from
      `tk-framework-shotgunutils.shotgun_model
      <https://developers.shotgridsoftware.com/tk-framework-shotgunutils/shotgun_model.html>`_
    - (instance-level) ``tk_multi_loader``, imported ``tk_multi_loader`` module


    """

    shotgun_globals = sgtk.platform.import_framework(
        "tk-framework-shotgunutils", "shotgun_globals"
    )
    shotgun_model = sgtk.platform.import_framework(
        "tk-framework-shotgunutils", "shotgun_model"
    )

    def __init__(
        self, parent: sgtk.platform.Application | sgtk.platform.Engine
    ) -> None:
        """Extend to set the ``tk_multi_loader`` instance attribute."""
        super().__init__(parent)
        self.tk_multi_loader = sgtk.platform.current_bundle().import_module(
            "tk_multi_loader"
        )

    def format_list_publish(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Get formatted texts for list view of the PublishedFile item at given index.

        ``show_sub_items`` is whether the "Show items in subfolders" checkbox is
        currently checked in the dialog.

        .. code-block:: text

            Layout of the list view in respect to returned (main_text, small_text):
             -------------------------------------------------
            | Thumbnail | main_text                           |
            |           | small_text                          |
             -------------------------------------------------
             -------------------------------------------------
            | Thumbnail | main_text                           |
            |           | small_text                          |
             -------------------------------------------------

        """
        sg_data = self.shotgun_model.get_sg_data(model_index)
        publish_type = self.shotgun_model.get_sanitized_data(
            model_index,
            self.tk_multi_loader.model_latestpublish.SgLatestPublishModel.PUBLISH_TYPE_NAME_ROLE,
        )

        main_text = "<b>%s</b>" % (sg_data.get("name") or "Unnamed")

        version = sg_data.get("version_number")
        vers_str = "%03d" % version if version is not None else "N/A"

        main_text += " Version %s" % vers_str

        # If we are in "show subfolders mode, this line will contain
        # the entity information (because we are displaying info from several entities
        # in a single view. If show subfolders mode is off, the latest description is shown.
        if show_sub_items:
            # show items in subfolders mode enabled
            # get the name of the associated entity

            main_text += "  ("

            entity_link = sg_data.get("entity")
            if entity_link:
                entity_link_type = self.shotgun_globals.get_type_display_name(
                    entity_link["type"]
                )
                main_text += "%s <span style='color:#2C93E2'>%s</span>" % (
                    entity_link_type,
                    entity_link["name"],
                )

            if sg_data.get("task") is not None:
                main_text += ", Task %s" % sg_data["task"]["name"]

            main_text += ")"
        elif sg_data.get("task") is not None:
            # When not in subfolders mode always show Task info
            # (similar to the logic in the thumbnail view, but always show)
            main_text += "  (Task %s)" % sg_data["task"]["name"]

        # Quicktime by John Smith at 2014-02-23 10:34
        created_unixtime = sg_data.get("created_at") or 0
        date_str = datetime.datetime.fromtimestamp(created_unixtime).strftime(
            "%Y-%m-%d %H:%M"
        )
        # created_by is set to None if the user has been deleted.
        if sg_data.get("created_by") and sg_data["created_by"].get("name"):
            author_str = sg_data["created_by"].get("name")
        else:
            author_str = "Unspecified User"
        small_text = "<span style='color:#2C93E2'>%s</span> by %s at %s" % (
            publish_type,
            author_str,
            date_str,
        )
        return main_text, small_text

    def format_list_folder(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Get formatted texts for list view of the folder item at given index.

        ``show_sub_items`` is whether the "Show items in subfolders" checkbox is
        currently checked in the dialog.

        .. code-block:: text

            Layout of the list view in respect to returned (main_text, small_text):
             -------------------------------------------------
            | Thumbnail | main_text                           |
            |           | small_text                          |
             -------------------------------------------------
             -------------------------------------------------
            | Thumbnail | main_text                           |
            |           | small_text                          |
             -------------------------------------------------

        """
        sg_data, field_value = self.tk_multi_loader.model_item_data.get_item_data(
            model_index
        )

        # by default, just display the value
        main_text = field_value
        small_text = ""

        if (
            isinstance(field_value, dict)
            and "name" in field_value
            and "type" in field_value
        ):
            # intermediate node with entity link
            field_value_type = self.shotgun_globals.get_type_display_name(
                field_value["type"]
            )

            main_text = "<b>%s</b> <b style='color:#2C93E2'>%s</b>" % (
                field_value_type,
                field_value["name"],
            )

        elif isinstance(field_value, list):
            # this is a list of some sort. Loop over all elements and extract a comma separated list.
            # this can be a multi link field but also a field like a tags field or a non-entity link type field.
            formatted_values = []
            formatted_types = set()

            for v in field_value:
                if isinstance(v, dict) and "name" in v and "type" in v:
                    # This is a link field
                    name = v["name"]
                    v_type = self.shotgun_globals.get_type_display_name(v["type"])
                    if name:
                        formatted_values.append(name)
                        formatted_types.add(v_type)
                else:
                    formatted_values.append(str(v))

            types = ", ".join(list(formatted_types))
            names = ", ".join(formatted_values)
            main_text = "<b>%s</b><br>%s" % (types, names)

        elif sg_data:
            # this is a leaf node
            display_name = self.shotgun_globals.get_type_display_name(sg_data["type"])
            main_text = "<b>%s</b> <b style='color:#2C93E2'>%s</b>" % (
                display_name,
                field_value,
            )
            small_text = sg_data.get("description") or "No description given."

        return main_text, small_text

    def format_thumbnail_publish(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Get thumbnail view texts for the PublishedFile item at given index.

        ``show_sub_items`` is whether the "Show items in subfolders" checkbox is
        currently checked in the dialog.

        .. code-block:: text

            Layout of the thumbnail view in respect to returned (header_text, details_text):
             --------------    --------------    --------------
            |              |  |              |  |              |
            |              |  |              |  |              |
            |  Thumbnail   |  |  Thumbnail   |  |  Thumbnail   |
            |              |  |              |  |              |
            |______________|  |______________|  |______________|
            | header_text  |  | header_text  |  | header_text  |
            | details_text |  | details_text |  | details_text |
             --------------    --------------    --------------

        """
        sg_data = self.shotgun_model.get_sg_data(model_index)
        publish_type = self.shotgun_model.get_sanitized_data(
            model_index,
            self.tk_multi_loader.model_latestpublish.SgLatestPublishModel.PUBLISH_TYPE_NAME_ROLE,
        )

        header_text = ""
        details_text = ""

        # get the name (lighting v3)
        name_str = "Unnamed"
        if sg_data.get("name"):
            name_str = sg_data.get("name")

        if sg_data.get("version_number"):
            name_str += " v%s" % sg_data.get("version_number")

        # now we are tracking whether this item has a unique task/name/type combo
        # or not via the specially injected task_uniqueness boolean.
        # If this is true, that means that this is the only item in the listing
        # with this name/type combo, and we can render its display name on two
        # lines, name first and then type, e.g.:
        # MyScene, v3
        # Maya Render
        #
        # However, there can be multiple *different* tasks which have the same
        # name/type combo - in this case, we want to display the task name too
        # since this is what differentiates the data. In that case we display it:
        # MyScene, v3 (Layout)
        # Maya Render
        #
        if sg_data.get("task_uniqueness") == False and sg_data.get("task") is not None:
            name_str += " (%s)" % sg_data["task"]["name"]

        # make this the title of the card
        header_text = name_str

        # check if we are in "deep mode". In that case, display the entity link info
        # on the thumb card. Otherwise, display the type.
        if show_sub_items:
            # display this publish in sub items node
            # in this case we want to display the following two lines
            # main_body v3
            # Shot AAA001

            # get the name of the associated entity
            entity_link = sg_data.get("entity")
            if entity_link is None:
                details_text = "Unlinked"
            else:
                entity_link_type = self.shotgun_globals.get_type_display_name(
                    entity_link["type"]
                )
                details_text = "%s %s" % (entity_link_type, entity_link["name"])

        else:
            # std publish - render with a name and a publish type
            # main_body v3
            # Render
            details_text = publish_type

        return header_text, details_text

    def format_thumbnail_folder(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Get thumbnail view texts for the folder item at given index.

        ``show_sub_items`` is whether the "Show items in subfolders" checkbox is
        currently checked in the dialog.

        .. code-block:: text

            Layout of the thumbnail view in respect to returned (header_text, details_text):
             --------------    --------------    --------------
            |              |  |              |  |              |
            |              |  |              |  |              |
            |  Thumbnail   |  |  Thumbnail   |  |  Thumbnail   |
            |              |  |              |  |              |
            |______________|  |______________|  |______________|
            | header_text  |  | header_text  |  | header_text  |
            | details_text |  | details_text |  | details_text |
             --------------    --------------    --------------

        """
        sg_data, field_value = self.tk_multi_loader.model_item_data.get_item_data(
            model_index
        )

        header_text = ""
        details_text = ""

        if (
            isinstance(field_value, dict)
            and "name" in field_value
            and "type" in field_value
        ):
            # intermediate node with entity link
            header_text = field_value["name"]
            details_text = self.shotgun_globals.get_type_display_name(
                field_value["type"]
            )

        elif isinstance(field_value, list):
            # this is a list of some sort. Loop over all elements and extract a comma separated list.
            formatted_values = []
            if len(field_value) == 0:
                # no items in list
                formatted_values.append("No Value")
            for v in field_value:
                if isinstance(v, dict) and "name" in v and "type" in v:
                    # This is a link field
                    if v.get("name"):
                        formatted_values.append(v.get("name"))
                else:
                    formatted_values.append(str(v))

            header_text = ", ".join(formatted_values)

        elif sg_data:
            # this is a leaf node
            header_text = field_value
            details_text = self.shotgun_globals.get_type_display_name(sg_data["type"])

        else:
            # other value (e.g. intermediary non-entity link node like sg_asset_type)
            header_text = field_value

        return header_text, details_text

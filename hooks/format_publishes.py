import sgtk

from sgtk.platform.qt import QtCore


class FormatPublishes(sgtk.get_hook_baseclass()):
    def format_list_publish(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Return formatted main and small text for the given publish folder."""
        return super().format_list_publish(model_index, show_sub_items=show_sub_items)

    def format_list_folder(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Return formatted main and small text for the given publish item."""
        return super().format_list_folder(model_index, show_sub_items=show_sub_items)

    def format_thumbnail_publish(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Return formatted header and body text for the given publish folder."""
        return super().format_thumbnail_publish(
            model_index, show_sub_items=show_sub_items
        )

    def format_thumbnail_folder(
        self, model_index: QtCore.QModelIndex, *, show_sub_items: bool = False
    ) -> tuple[str, str]:
        """Return formatted header and body text for the given publish item."""
        return super().format_thumbnail_folder(
            model_index, show_sub_items=show_sub_items
        )

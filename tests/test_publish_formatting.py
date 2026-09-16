# Copyright (c) 2026 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.

"""Unit test the formatted text of ``SgPublish*Delegate._format_*()``.

This is to ensure we have a reference output to check future refactoring against v1.25.6
so lots of values are baked into the test data.

Note:
    Tank test classes that subclass ``TankTestBase`` must also import ``setUpModule`` as
    into this module's namespace. Also more than 1 _fork_ in sub-classing/descendants
    per module will break the setup/teardown.

"""

import contextlib
from typing import NamedTuple
from types import ModuleType
from unittest import mock

from test_api import AppTestBase, setUpModule  # noqa


class Binding(NamedTuple):
    """Attributes to bind for ``mocked_model_item_data_widget``."""

    delegate: object
    shotgun_model: ModuleType
    SgLatestPublishModel: type
    model_item_data: ModuleType

    @classmethod
    def from_delegate_module(cls, delegate, module):
        if hook := getattr(delegate, "_format_hook", None):
            shotgun_model = hook.shotgun_model
            SgLatestPublishModel = (
                hook.tk_multi_loader.model_latestpublish.SgLatestPublishModel
            )
            model_item_data = hook.tk_multi_loader.model_item_data
        else:
            shotgun_model = module.shotgun_model
            SgLatestPublishModel = module.SgLatestPublishModel
            model_item_data = module.model_item_data

        return cls(
            delegate=delegate,
            shotgun_model=shotgun_model,
            SgLatestPublishModel=SgLatestPublishModel,
            model_item_data=model_item_data,
        )


@contextlib.contextmanager
def mocked_model_item_data_widget(binding: Binding, field_value):
    mock_model_index = mock.MagicMock()
    mock_widget = mock.MagicMock()
    mock_widget.set_text = mock.MagicMock()

    pub_type_str = "Flame Render"
    sg_data = {
        "code": "aaa_00010_F004_C003_0228F8_v000.%04d.dpx",
        "created_at": 1425378837.0,
        "created_by": {"id": 42, "name": "Manne Ohrstrom", "type": "HumanUser"},
        "created_by.HumanUser.image": "https://...",
        "description": "testing testing, 1,2,3",
        "entity": {"id": 1660, "name": "aaa_00010", "type": "Shot"},
        "id": 1340,
        "image": "https:...",
        "name": "aaa_00010, F004_C003_0228F8",
        "path": {
            "content_type": "image/dpx",
            "id": 24116,
            "link_type": "local",
            "local_path": "/mnt/projects...",
            "local_path_linux": "/mnt/projects...",
            "local_path_mac": "/mnt/projects...",
            "local_path_windows": "z:\\mnt\\projects...",
            "local_storage": {"id": 4, "name": "primary", "type": "LocalStorage"},
            "name": "aaa_00010_F004_C003_0228F8_v000.%04d.dpx",
            "type": "Attachment",
            "url": "file:///mnt/projects...",
        },
        "project": {"id": 289, "name": "Climp", "type": "Project"},
        "published_file_type": {
            "id": 53,
            "name": pub_type_str,
            "type": "PublishedFileType",
        },
        "task": None,
        "task.Task.content": None,
        "task.Task.due_date": None,
        "task.Task.sg_status_list": None,
        "task_uniqueness": False,
        "type": "PublishedFile",
        "version": {
            "id": 6697,
            "name": "aaa_00010_F004_C003_0228F8_v000",
            "type": "Version",
        },
        "version.Version.sg_status_list": "rev",
        "version_number": 2,
    }

    original_get_sanitized_data = binding.shotgun_model.get_sanitized_data

    def mock_get_sanitized_data(model_index, role):
        return (
            pub_type_str
            if model_index is mock_model_index
            and role == binding.SgLatestPublishModel.PUBLISH_TYPE_NAME_ROLE
            else original_get_sanitized_data(model_index)
        )

    original_get_sg_data = binding.shotgun_model.get_sg_data

    def mock_get_sg_data(model_index):
        return (
            sg_data
            if model_index is mock_model_index
            else original_get_sg_data(model_index)
        )

    original_get_item_data = binding.model_item_data.get_item_data

    def mock_get_item_data(model_index):
        return (
            (sg_data, field_value)
            if model_index is mock_model_index
            else original_get_item_data(model_index)
        )

    with (
        mock.patch.object(
            binding.model_item_data,
            "get_item_data",
            mock_get_item_data,
        ),
        mock.patch.multiple(
            binding.shotgun_model,
            get_sg_data=mock_get_sg_data,
            get_sanitized_data=mock_get_sanitized_data,
        ),
    ):
        yield mock_model_index, mock_widget

    call_args = mock_widget.set_text.call_args
    assert call_args is not None
    assert call_args.args and len(call_args.args) == 2


def check_delegate_text(
    binding: Binding,
    field_value: object,
    folder_main: str,
    folder_small: str,
    publish_main: str,
    publish_small: str,
    *,
    show_sub_items: bool = False,
) -> None:
    with mock.patch.object(binding.delegate, "_sub_items_mode", show_sub_items):
        with mocked_model_item_data_widget(binding, field_value) as (
            model_index,
            mock_widget,
        ):
            binding.delegate._format_folder(model_index, mock_widget)

        main_text, small_text = mock_widget.set_text.call_args.args
        assert main_text == folder_main
        assert small_text == folder_small

        with mocked_model_item_data_widget(binding, field_value) as (
            model_index,
            mock_widget,
        ):
            binding.delegate._format_publish(model_index, mock_widget)

        main_text, small_text = mock_widget.set_text.call_args.args
        assert main_text == publish_main
        assert small_text == publish_small


class TestDelegatesPublishFormatting(AppTestBase):
    def setUp(self):
        super().setUp()
        from sgtk.platform.qt import QtCore, QtGui

        dummy_view = QtGui.QListView()

        tk_multi_loader = self.app.import_module("tk_multi_loader")
        list_cls = tk_multi_loader.delegate_publish_list.SgPublishListDelegate
        thumb_cls = tk_multi_loader.delegate_publish_thumb.SgPublishThumbDelegate

        self.QtCore = QtCore
        self.QtGui = QtGui
        self.list_module = tk_multi_loader.delegate_publish_list
        self.thumb_module = tk_multi_loader.delegate_publish_thumb

        self.list_delegate = list_cls(dummy_view, mock.MagicMock())
        self.thumb_delegate = thumb_cls(dummy_view, mock.MagicMock())

        self.list_binding = Binding.from_delegate_module(
            self.list_delegate, self.list_module
        )
        self.thumb_binding = Binding.from_delegate_module(
            self.thumb_delegate, self.thumb_module
        )

    def test_methods_exist(self):
        """Ensure no internal API methods are missing."""
        assert callable(self.list_delegate._format_folder)
        assert callable(self.list_delegate._format_publish)
        assert callable(self.thumb_delegate._format_folder)
        assert callable(self.thumb_delegate._format_publish)

    def test_list_dict(self):
        field_value = {
            "id": 6697,
            "name": "aaa_00010_F004_C003_0228F8_v000",
            "type": "Version",
        }
        folder_main = (
            f"<b>Version</b> <b style='color:#2C93E2'>{field_value['name']}</b>"
        )
        check_delegate_text(
            self.list_binding,
            field_value,
            folder_main,
            "",
            "<b>aaa_00010, F004_C003_0228F8</b> Version 002  (Shot <span style='color:#2C93E2'>aaa_00010</span>)",
            "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33",
            show_sub_items=True,
        )
        check_delegate_text(
            self.list_binding,
            field_value,
            folder_main,
            "",
            "<b>aaa_00010, F004_C003_0228F8</b> Version 002",
            "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33",
            show_sub_items=False,
        )

    def test_list_list_of_entities(self):
        field_value = [
            {
                "id": 6697,
                "name": "aaa_00010_F004_C003_0228F8_v000",
                "type": "Version",
            },
            {
                "id": 6698,
                "name": "aaa_00020_F004_C003_0228F8_v000",
                "type": "Version",
            },
        ]
        folder_main = (
            "<b>Version</b>"
            "<br>aaa_00010_F004_C003_0228F8_v000, aaa_00020_F004_C003_0228F8_v000"
        )
        check_delegate_text(
            self.list_binding,
            field_value,
            folder_main,
            "",
            "<b>aaa_00010, F004_C003_0228F8</b> Version 002  (Shot <span style='color:#2C93E2'>aaa_00010</span>)",
            "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33",
            show_sub_items=True,
        )
        check_delegate_text(
            self.list_binding,
            field_value,
            folder_main,
            "",
            "<b>aaa_00010, F004_C003_0228F8</b> Version 002",
            "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33",
            show_sub_items=False,
        )

    def test_list_list_of_values(self):
        field_value = [None, 123, "abc"]
        folder_main = "<b></b><br>None, 123, abc"
        check_delegate_text(
            self.list_binding,
            field_value,
            folder_main,
            "",
            "<b>aaa_00010, F004_C003_0228F8</b> Version 002  (Shot <span style='color:#2C93E2'>aaa_00010</span>)",
            "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33",
            show_sub_items=True,
        )
        check_delegate_text(
            self.list_binding,
            field_value,
            folder_main,
            "",
            "<b>aaa_00010, F004_C003_0228F8</b> Version 002",
            "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33",
            show_sub_items=False,
        )

    def test_thumb_dict(self):
        field_value = {
            "id": 6697,
            "name": "aaa_00010_F004_C003_0228F8_v000",
            "type": "Version",
        }
        check_delegate_text(
            self.thumb_binding,
            field_value,
            field_value["name"],
            field_value["type"],
            "aaa_00010, F004_C003_0228F8 v2",
            "Shot aaa_00010",
            show_sub_items=True,
        )
        check_delegate_text(
            self.thumb_binding,
            field_value,
            field_value["name"],
            field_value["type"],
            "aaa_00010, F004_C003_0228F8 v2",
            "Flame Render",
            show_sub_items=False,
        )

    def test_thumb_list_of_entities(self):
        field_value = [
            {
                "id": 6697,
                "name": "aaa_00010_F004_C003_0228F8_v000",
                "type": "Version",
            },
            {
                "id": 6698,
                "name": "aaa_00020_F004_C003_0228F8_v000",
                "type": "Version",
            },
        ]
        folder_main = "aaa_00010_F004_C003_0228F8_v000, aaa_00020_F004_C003_0228F8_v000"
        check_delegate_text(
            self.thumb_binding,
            field_value,
            folder_main,
            "",
            "aaa_00010, F004_C003_0228F8 v2",
            "Shot aaa_00010",
            show_sub_items=True,
        )
        check_delegate_text(
            self.thumb_binding,
            field_value,
            folder_main,
            "",
            "aaa_00010, F004_C003_0228F8 v2",
            "Flame Render",
            show_sub_items=False,
        )

    def test_thumb_list_of_values(self):
        field_value = [None, 123, "abc"]
        folder_main = "None, 123, abc"
        check_delegate_text(
            self.thumb_binding,
            field_value,
            folder_main,
            "",
            "aaa_00010, F004_C003_0228F8 v2",
            "Shot aaa_00010",
            show_sub_items=True,
        )
        check_delegate_text(
            self.thumb_binding,
            field_value,
            folder_main,
            "",
            "aaa_00010, F004_C003_0228F8 v2",
            "Flame Render",
            show_sub_items=False,
        )

"""Unit test the formatted text of ``SgPublish*Delegate._format_*()``.

This is to ensure we have a reference output to check future refactoring against, so
lots of values are baked into the test data.

Note:
    Tank test classes that subclass ``TankTestBase`` must also import ``setUpModule`` as
    into this module's namespace. Also more than 1 _fork_ in sub-classing/descendants
    per module will break the setup/teardown.

"""

import contextlib
from unittest import mock

from test_api import AppTestBase, setUpModule  # noqa


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

    def test_methods_exist(self):
        assert callable(self.list_delegate._format_folder)
        assert callable(self.list_delegate._format_publish)
        assert callable(self.thumb_delegate._format_folder)
        assert callable(self.thumb_delegate._format_publish)

    @contextlib.contextmanager
    def mocked_model_item_data_widget(self, hook, field_value):
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

        original_get_sanitized_data = hook.shotgun_model.get_sanitized_data
        model_cls = hook.tk_multi_loader.model_latestpublish.SgLatestPublishModel

        def mock_get_sanitized_data(model_index, role):
            return (
                pub_type_str
                if model_index is mock_model_index
                and role == model_cls.PUBLISH_TYPE_NAME_ROLE
                else original_get_sanitized_data(model_index)
            )

        original_get_sg_data = hook.shotgun_model.get_sg_data

        def mock_get_sg_data(model_index):
            return (
                sg_data
                if model_index is mock_model_index
                else original_get_sg_data(model_index)
            )

        original_get_item_data = hook.tk_multi_loader.model_item_data.get_item_data

        def mock_get_item_data(model_index):
            return (
                (sg_data, field_value)
                if model_index is mock_model_index
                else original_get_item_data(model_index)
            )

        with (
            mock.patch.object(
                hook.tk_multi_loader.model_item_data,
                "get_item_data",
                mock_get_item_data,
            ),
            mock.patch.multiple(
                hook.shotgun_model,
                get_sg_data=mock_get_sg_data,
                get_sanitized_data=mock_get_sanitized_data,
            ),
        ):
            yield mock_model_index, mock_widget

        call_args = mock_widget.set_text.call_args
        assert call_args is not None
        assert call_args.args and len(call_args.args) == 2

    def test_list(self):
        # an Entity
        field_value = {
            "id": 6697,
            "name": "aaa_00010_F004_C003_0228F8_v000",
            "type": "Version",
        }
        folder_main = "<b>Version</b> <b style='color:#2C93E2'>aaa_00010_F004_C003_0228F8_v000</b>"
        folder_small = ""
        publish_main = "<b>aaa_00010, F004_C003_0228F8</b> Version 002"
        publish_small = "<span style='color:#2C93E2'>Flame Render</span> by Manne Ohrstrom at 2015-03-03 10:33"

        list_hook = self.list_delegate._format_hook
        with self.mocked_model_item_data_widget(list_hook, field_value) as (
            model_index,
            mock_widget,
        ):
            self.list_delegate._format_folder(model_index, mock_widget)

        main_text, small_text = mock_widget.set_text.call_args.args
        assert main_text == folder_main
        assert small_text == folder_small

        with self.mocked_model_item_data_widget(list_hook, field_value) as (
            model_index,
            mock_widget,
        ):
            self.list_delegate._format_publish(model_index, mock_widget)

        main_text, small_text = mock_widget.set_text.call_args.args
        assert main_text == publish_main
        assert small_text == publish_small

    def test_thumb(self):
        # an Entity
        field_value = {
            "id": 6697,
            "name": "aaa_00010_F004_C003_0228F8_v000",
            "type": "Version",
        }
        folder_main = field_value["name"]
        folder_small = field_value["type"]
        publish_main = "aaa_00010, F004_C003_0228F8 v2"
        publish_small = "Flame Render"

        thumb_hook = self.thumb_delegate._format_hook
        with self.mocked_model_item_data_widget(thumb_hook, field_value) as (
            model_index,
            mock_widget,
        ):
            self.thumb_delegate._format_folder(model_index, mock_widget)

        main_text, small_text = mock_widget.set_text.call_args.args
        assert main_text == folder_main
        assert small_text == folder_small

        with self.mocked_model_item_data_widget(thumb_hook, field_value) as (
            model_index,
            mock_widget,
        ):
            self.thumb_delegate._format_publish(model_index, mock_widget)

        main_text, small_text = mock_widget.set_text.call_args.args
        assert main_text == publish_main
        assert small_text == publish_small

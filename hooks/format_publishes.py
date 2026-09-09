import datetime

import sgtk

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)


class FormatPublishes(sgtk.get_hook_baseclass()):
    def format_list_publish(self, sg_data: dict, publish_type: str) -> tuple[str, str]:
        """Return formatted main and small text for the given publish folder."""
        main_text = "<b>%s</b>" % (sg_data.get("name") or "Unnamed")

        version = sg_data.get("version_number")
        vers_str = "%03d" % version if version is not None else "N/A"

        main_text += " Version %s" % vers_str

        # If we are in "show subfolders mode, this line will contain
        # the entity information (because we are displaying info from several entities
        # in a single view. If show subfolders mode is off, the latest description is shown.
        if self._sub_items_mode:
            # show items in subfolders mode enabled
            # get the name of the associated entity

            main_text += "  ("

            entity_link = sg_data.get("entity")
            if entity_link:
                entity_link_type = shotgun_globals.get_type_display_name(
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

    def format_list_folder(self, sg_data: dict, field_value: object) -> tuple[str, str]:
        """Return formatted main and small text for the given publish item."""

        # by default, just display the value
        main_text = field_value
        small_text = ""

        if (
            isinstance(field_value, dict)
            and "name" in field_value
            and "type" in field_value
        ):
            # intermediate node with entity link
            field_value_type = shotgun_globals.get_type_display_name(
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
                    v_type = shotgun_globals.get_type_display_name(v["type"])
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
            display_name = shotgun_globals.get_type_display_name(sg_data["type"])
            main_text = "<b>%s</b> <b style='color:#2C93E2'>%s</b>" % (
                display_name,
                field_value,
            )
            small_text = sg_data.get("description") or "No description given."

        return main_text, small_text

    def format_thumbnail_publish(
        self, sg_data: dict, publish_type: str
    ) -> tuple[str, str]:
        """Return formatted header and body text for the given publish folder."""
        header_text = ""
        details_text = ""

        # example data:

        # {'code': 'aaa_00010_F004_C003_0228F8_v000.%04d.dpx',
        #  'created_at': 1425378837.0,
        #  'created_by': {'id': 42, 'name': 'Manne Ohrstrom', 'type': 'HumanUser'},
        #  'created_by.HumanUser.image': 'https://...',
        #  'description': 'testing testing, 1,2,3',
        #  'entity': {'id': 1660, 'name': 'aaa_00010', 'type': 'Shot'},
        #  'id': 1340,
        #  'image': 'https:...',
        #  'name': 'aaa_00010, F004_C003_0228F8',
        #  'path': {'content_type': 'image/dpx',
        #           'id': 24116,
        #           'link_type': 'local',
        #           'local_path': '/mnt/projects...',
        #           'local_path_linux': '/mnt/projects...',
        #           'local_path_mac': '/mnt/projects...',
        #           'local_path_windows': 'z:\\mnt\\projects...',
        #           'local_storage': {'id': 4,
        #                             'name': 'primary',
        #                             'type': 'LocalStorage'},
        #           'name': 'aaa_00010_F004_C003_0228F8_v000.%04d.dpx',
        #           'type': 'Attachment',
        #           'url': 'file:///mnt/projects...'},
        #  'project': {'id': 289, 'name': 'Climp', 'type': 'Project'},
        #  'published_file_type': {'id': 53,
        #                          'name': 'Flame Render',
        #                          'type': 'PublishedFileType'},
        #  'task': None,
        #  'task.Task.content': None,
        #  'task.Task.due_date': None,
        #  'task.Task.sg_status_list': None,
        #  'task_uniqueness': False,
        #  'type': 'PublishedFile',
        #  'version': {'id': 6697,
        #              'name': 'aaa_00010_F004_C003_0228F8_v000',
        #              'type': 'Version'},
        #  'version.Version.sg_status_list': 'rev',
        #  'version_number': 2}

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
        if self._sub_items_mode:
            # display this publish in sub items node
            # in this case we want to display the following two lines
            # main_body v3
            # Shot AAA001

            # get the name of the associated entity
            entity_link = sg_data.get("entity")
            if entity_link is None:
                details_text = "Unlinked"
            else:
                entity_link_type = shotgun_globals.get_type_display_name(
                    entity_link["type"]
                )
                details_text = "%s %s" % (entity_link_type, entity_link["name"])

        else:
            # std publish - render with a name and a publish type
            # main_body v3
            # Render
            details_text = publish_type

        return header_text, details_text

    def format_thumbnail_folder(self, sg_data: dict, field_value) -> tuple[str, str]:
        """Return formatted header and body text for the given publish item."""
        header_text = ""
        details_text = ""

        if (
            isinstance(field_value, dict)
            and "name" in field_value
            and "type" in field_value
        ):
            # intermediate node with entity link
            header_text = field_value["name"]
            details_text = shotgun_globals.get_type_display_name(field_value["type"])

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
            details_text = shotgun_globals.get_type_display_name(sg_data["type"])

        else:
            # other value (e.g. intermediary non-entity link node like sg_asset_type)
            header_text = field_value

        return header_text, details_text

# Copyright (c) 2026 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
"""Hook for formatting the folder/PublishedFile item widgets in the loader.

Here we only simply serve as a pass-through for the default formatting logic in
``tk_multi_loader.hooks.format_publishes.BaseFormatPublishes``.

It's up to the subclass to decide on which methods to override or extend

"""

import sgtk


class FormatPublishes(sgtk.get_hook_baseclass()):
    """ "Simple pass through for the default, base formatting logic.

    See ``tk_multi_loader.hooks.format_publishes.BaseFormatPublishes``.
    """

# compat_qt.py
#
# Compatibilité Qt5 / Qt6 pour plugins QGIS
#
# Fonctionne avec :
# - QGIS3 / PyQt5
# - QGIS4 / PyQt6
#
# Usage :
#
# from .compat_qt import *
#
# item.setCheckState(CHECKED)
# header.setSectionResizeMode(HEADER_STRETCH)
# if role == DISPLAY_ROLE:
#     ...
#

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox)


# =============================================================================
# Qt version detection
# =============================================================================

IS_QT6 = hasattr(Qt, "CheckState")


# =============================================================================
# CheckState
# =============================================================================

if IS_QT6:
    CHECKED = Qt.CheckState.Checked
    UNCHECKED = Qt.CheckState.Unchecked
    PARTIALLY_CHECKED = Qt.CheckState.PartiallyChecked
else:
    CHECKED = Qt.Checked
    UNCHECKED = Qt.Unchecked
    PARTIALLY_CHECKED = Qt.PartiallyChecked


# =============================================================================
# Orientation
# =============================================================================

if IS_QT6:
    HORIZONTAL = Qt.Orientation.Horizontal
    VERTICAL = Qt.Orientation.Vertical
else:
    HORIZONTAL = Qt.Horizontal
    VERTICAL = Qt.Vertical


# =============================================================================
# Alignment
# =============================================================================

if IS_QT6:
    ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
    ALIGN_RIGHT = Qt.AlignmentFlag.AlignRight
    ALIGN_HCENTER = Qt.AlignmentFlag.AlignHCenter
    ALIGN_VCENTER = Qt.AlignmentFlag.AlignVCenter
    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    ALIGN_TOP = Qt.AlignmentFlag.AlignTop
    ALIGN_BOTTOM = Qt.AlignmentFlag.AlignBottom
else:
    ALIGN_LEFT = Qt.AlignLeft
    ALIGN_RIGHT = Qt.AlignRight
    ALIGN_HCENTER = Qt.AlignHCenter
    ALIGN_VCENTER = Qt.AlignVCenter
    ALIGN_CENTER = Qt.AlignCenter
    ALIGN_TOP = Qt.AlignTop
    ALIGN_BOTTOM = Qt.AlignBottom


# =============================================================================
# ItemDataRole
# =============================================================================

if IS_QT6:
    DISPLAY_ROLE = Qt.ItemDataRole.DisplayRole
    EDIT_ROLE = Qt.ItemDataRole.EditRole
    TOOLTIP_ROLE = Qt.ItemDataRole.ToolTipRole
    STATUS_TIP_ROLE = Qt.ItemDataRole.StatusTipRole
    WHATS_THIS_ROLE = Qt.ItemDataRole.WhatsThisRole
    DECORATION_ROLE = Qt.ItemDataRole.DecorationRole
    TEXT_ALIGNMENT_ROLE = Qt.ItemDataRole.TextAlignmentRole
    BACKGROUND_ROLE = Qt.ItemDataRole.BackgroundRole
    FOREGROUND_ROLE = Qt.ItemDataRole.ForegroundRole
    CHECKSTATE_ROLE = Qt.ItemDataRole.CheckStateRole
    USER_ROLE = Qt.ItemDataRole.UserRole
else:
    DISPLAY_ROLE = Qt.DisplayRole
    EDIT_ROLE = Qt.EditRole
    TOOLTIP_ROLE = Qt.ToolTipRole
    STATUS_TIP_ROLE = Qt.StatusTipRole
    WHATS_THIS_ROLE = Qt.WhatsThisRole
    DECORATION_ROLE = Qt.DecorationRole
    TEXT_ALIGNMENT_ROLE = Qt.TextAlignmentRole
    BACKGROUND_ROLE = Qt.BackgroundRole
    FOREGROUND_ROLE = Qt.ForegroundRole
    CHECKSTATE_ROLE = Qt.CheckStateRole
    USER_ROLE = Qt.UserRole


# =============================================================================
# ItemFlags
# =============================================================================

if IS_QT6:
    ITEM_IS_SELECTABLE = Qt.ItemFlag.ItemIsSelectable
    ITEM_IS_EDITABLE = Qt.ItemFlag.ItemIsEditable
    ITEM_IS_DRAG_ENABLED = Qt.ItemFlag.ItemIsDragEnabled
    ITEM_IS_DROP_ENABLED = Qt.ItemFlag.ItemIsDropEnabled
    ITEM_IS_USER_CHECKABLE = Qt.ItemFlag.ItemIsUserCheckable
    ITEM_IS_ENABLED = Qt.ItemFlag.ItemIsEnabled
    ITEM_IS_AUTO_TRISTATE = Qt.ItemFlag.ItemIsAutoTristate
    ITEM_NEVER_HAS_CHILDREN = Qt.ItemFlag.ItemNeverHasChildren
    ITEM_IS_USER_TRISTATE = Qt.ItemFlag.ItemIsUserTristate
else:
    ITEM_IS_SELECTABLE = Qt.ItemIsSelectable
    ITEM_IS_EDITABLE = Qt.ItemIsEditable
    ITEM_IS_DRAG_ENABLED = Qt.ItemIsDragEnabled
    ITEM_IS_DROP_ENABLED = Qt.ItemIsDropEnabled
    ITEM_IS_USER_CHECKABLE = Qt.ItemIsUserCheckable
    ITEM_IS_ENABLED = Qt.ItemIsEnabled
    ITEM_IS_AUTO_TRISTATE = Qt.ItemIsAutoTristate
    ITEM_NEVER_HAS_CHILDREN = Qt.ItemNeverHasChildren
    ITEM_IS_USER_TRISTATE = Qt.ItemIsUserTristate


# =============================================================================
# SortOrder
# =============================================================================

if IS_QT6:
    ASCENDING_ORDER = Qt.SortOrder.AscendingOrder
    DESCENDING_ORDER = Qt.SortOrder.DescendingOrder
else:
    ASCENDING_ORDER = Qt.AscendingOrder
    DESCENDING_ORDER = Qt.DescendingOrder


# =============================================================================
# ContextMenuPolicy
# =============================================================================

if IS_QT6:
    CUSTOM_CONTEXT_MENU = Qt.ContextMenuPolicy.CustomContextMenu
else:
    CUSTOM_CONTEXT_MENU = Qt.CustomContextMenu


# =============================================================================
# WindowModality
# =============================================================================

if IS_QT6:
    APPLICATION_MODAL = Qt.WindowModality.ApplicationModal
    WINDOW_MODAL = Qt.WindowModality.WindowModal
    NON_MODAL = Qt.WindowModality.NonModal
else:
    APPLICATION_MODAL = Qt.ApplicationModal
    WINDOW_MODAL = Qt.WindowModal
    NON_MODAL = Qt.NonModal


# =============================================================================
# Keyboard modifiers
# =============================================================================

if IS_QT6:
    CONTROL_MODIFIER = Qt.KeyboardModifier.ControlModifier
    SHIFT_MODIFIER = Qt.KeyboardModifier.ShiftModifier
    ALT_MODIFIER = Qt.KeyboardModifier.AltModifier
else:
    CONTROL_MODIFIER = Qt.ControlModifier
    SHIFT_MODIFIER = Qt.ShiftModifier
    ALT_MODIFIER = Qt.AltModifier


# =============================================================================
# Mouse buttons
# =============================================================================

if IS_QT6:
    LEFT_BUTTON = Qt.MouseButton.LeftButton
    RIGHT_BUTTON = Qt.MouseButton.RightButton
    MIDDLE_BUTTON = Qt.MouseButton.MiddleButton
else:
    LEFT_BUTTON = Qt.LeftButton
    RIGHT_BUTTON = Qt.RightButton
    MIDDLE_BUTTON = Qt.MidButton


# =============================================================================
# Pen styles
# =============================================================================

if IS_QT6:
    SOLID_LINE = Qt.PenStyle.SolidLine
    DASH_LINE = Qt.PenStyle.DashLine
    DOT_LINE = Qt.PenStyle.DotLine
else:
    SOLID_LINE = Qt.SolidLine
    DASH_LINE = Qt.DashLine
    DOT_LINE = Qt.DotLine


# =============================================================================
# Brush styles
# =============================================================================

if IS_QT6:
    NO_BRUSH = Qt.BrushStyle.NoBrush
    SOLID_PATTERN = Qt.BrushStyle.SolidPattern
else:
    NO_BRUSH = Qt.NoBrush
    SOLID_PATTERN = Qt.SolidPattern


# =============================================================================
# ScrollMode
# =============================================================================

if IS_QT6:
    SCROLL_PER_ITEM = QAbstractItemView.ScrollMode.ScrollPerItem
    SCROLL_PER_PIXEL = QAbstractItemView.ScrollMode.ScrollPerPixel
else:
    SCROLL_PER_ITEM = QAbstractItemView.ScrollPerItem
    SCROLL_PER_PIXEL = QAbstractItemView.ScrollPerPixel


# =============================================================================
# SelectionMode
# =============================================================================

if IS_QT6:
    NO_SELECTION = QAbstractItemView.SelectionMode.NoSelection
    SINGLE_SELECTION = QAbstractItemView.SelectionMode.SingleSelection
    MULTI_SELECTION = QAbstractItemView.SelectionMode.MultiSelection
    EXTENDED_SELECTION = QAbstractItemView.SelectionMode.ExtendedSelection
else:
    NO_SELECTION = QAbstractItemView.NoSelection
    SINGLE_SELECTION = QAbstractItemView.SingleSelection
    MULTI_SELECTION = QAbstractItemView.MultiSelection
    EXTENDED_SELECTION = QAbstractItemView.ExtendedSelection


# =============================================================================
# SelectionBehavior
# =============================================================================

if IS_QT6:
    SELECT_ITEMS = QAbstractItemView.SelectionBehavior.SelectItems
    SELECT_ROWS = QAbstractItemView.SelectionBehavior.SelectRows
    SELECT_COLUMNS = QAbstractItemView.SelectionBehavior.SelectColumns
else:
    SELECT_ITEMS = QAbstractItemView.SelectItems
    SELECT_ROWS = QAbstractItemView.SelectRows
    SELECT_COLUMNS = QAbstractItemView.SelectColumns


# =============================================================================
# EditTrigger
# =============================================================================

if IS_QT6:
    NO_EDIT_TRIGGERS = QAbstractItemView.EditTrigger.NoEditTriggers
    CURRENT_CHANGED = QAbstractItemView.EditTrigger.CurrentChanged
    DOUBLE_CLICKED = QAbstractItemView.EditTrigger.DoubleClicked
    SELECTED_CLICKED = QAbstractItemView.EditTrigger.SelectedClicked
else:
    NO_EDIT_TRIGGERS = QAbstractItemView.NoEditTriggers
    CURRENT_CHANGED = QAbstractItemView.CurrentChanged
    DOUBLE_CLICKED = QAbstractItemView.DoubleClicked
    SELECTED_CLICKED = QAbstractItemView.SelectedClicked


# =============================================================================
# DragDropMode
# =============================================================================

if IS_QT6:
    NO_DRAG_DROP = QAbstractItemView.DragDropMode.NoDragDrop
    DRAG_ONLY = QAbstractItemView.DragDropMode.DragOnly
    DROP_ONLY = QAbstractItemView.DragDropMode.DropOnly
    DRAG_DROP = QAbstractItemView.DragDropMode.DragDrop
    INTERNAL_MOVE = QAbstractItemView.DragDropMode.InternalMove
else:
    NO_DRAG_DROP = QAbstractItemView.NoDragDrop
    DRAG_ONLY = QAbstractItemView.DragOnly
    DROP_ONLY = QAbstractItemView.DropOnly
    DRAG_DROP = QAbstractItemView.DragDrop
    INTERNAL_MOVE = QAbstractItemView.InternalMove


# =============================================================================
# Header resize modes
# =============================================================================

if IS_QT6:
    HEADER_INTERACTIVE = QHeaderView.ResizeMode.Interactive
    HEADER_FIXED = QHeaderView.ResizeMode.Fixed
    HEADER_STRETCH = QHeaderView.ResizeMode.Stretch
    HEADER_RESIZE_TO_CONTENTS = QHeaderView.ResizeMode.ResizeToContents
else:
    HEADER_INTERACTIVE = QHeaderView.Interactive
    HEADER_FIXED = QHeaderView.Fixed
    HEADER_STRETCH = QHeaderView.Stretch
    HEADER_RESIZE_TO_CONTENTS = QHeaderView.ResizeToContents


# =============================================================================
# MessageBox
# =============================================================================

if IS_QT6:
    MSG_YES = QMessageBox.StandardButton.Yes
    MSG_NO = QMessageBox.StandardButton.No
    MSG_OK = QMessageBox.StandardButton.Ok
else:
    MSG_YES = QMessageBox.Yes
    MSG_NO = QMessageBox.No
    MSG_OK = QMessageBox.Ok
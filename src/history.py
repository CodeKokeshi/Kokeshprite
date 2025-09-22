from PyQt6.QtGui import QPixmap

class HistoryManager:
    """Manages undo/redo history for the canvas using pixmap snapshots.
    Strategy:
      - Store QPixmap copies after completed operations (stroke, fill, clear).
      - Undo pops from undo stack to redo stack; redo pops from redo stack back to undo.
    """

    def __init__(self, max_depth: int = 100):
        self.max_depth = max_depth
        self._undo_stack: list[QPixmap] = []
        self._redo_stack: list[QPixmap] = []

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def push(self, pixmap: QPixmap):
        # Clone the pixmap to decouple from future mutations
        self._undo_stack.append(QPixmap(pixmap))
        if len(self._undo_stack) > self.max_depth:
            self._undo_stack.pop(0)
        # New action invalidates redo history
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 1  # Keep first as baseline

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self) -> QPixmap | None:
        if not self.can_undo():
            return None
        # Move current state to redo and return previous
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return QPixmap(self._undo_stack[-1])

    def redo(self) -> QPixmap | None:
        if not self.can_redo():
            return None
        state = self._redo_stack.pop()
        self._undo_stack.append(state)
        return QPixmap(state)

    def snapshot_count(self) -> int:
        return len(self._undo_stack)

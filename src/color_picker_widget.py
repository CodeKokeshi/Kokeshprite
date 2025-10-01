from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLineEdit,
    QLabel,
    QSizePolicy,
    QStyle,
    QStyleOptionSlider,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression, QRect, QRectF, QSize
from PyQt6.QtGui import (
    QColor,
    QImage,
    QPainter,
    QPen,
    QRegularExpressionValidator,
    QLinearGradient,
    QPixmap,
    QPainterPath,
)


class _SVCanvas(QWidget):
    svChanged = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        # RESPONSIVE: Adapt to available space
        self.setMinimumSize(80, 80)   # Smaller minimum for tight spaces
        self.setMaximumSize(160, 160) # Larger maximum when space available
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._hue = 0
        self._saturation = 1.0
        self._value = 1.0
        self._image = None

    def set_hue(self, hue: float):
        if hue == self._hue and self._image is not None:
            return
        self._hue = hue
        self._generate_image()
        self.update()

    def set_sv(self, saturation: float, value: float):
        self._saturation = max(0.0, min(1.0, saturation))
        self._value = max(0.0, min(1.0, value))
        self.update()

    def _generate_image(self):
        width = max(1, self.width())
        height = max(1, self.height())
        img = QImage(width, height, QImage.Format.Format_RGB32)
        for y in range(height):
            v = 1.0 - (y / (height - 1)) if height > 1 else 1.0
            for x in range(width):
                s = x / (width - 1) if width > 1 else 0
                color = QColor()
                color.setHsvF(self._hue / 360.0, s, v)
                img.setPixelColor(x, y, color)
        self._image = img

    def sizeHint(self):
        # RESPONSIVE: Size based on available space
        return QSize(100, 100)  # Balanced default size

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._generate_image()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._image is None:
            self._generate_image()
        if self._image is not None:
            painter.drawImage(self.rect(), self._image, self._image.rect())
        # Draw selection marker
        sx = int(self._saturation * (self.width() - 1))
        sy = int((1.0 - self._value) * (self.height() - 1))
        marker_rect = QRect(sx - 5, sy - 5, 10, 10)
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(marker_rect)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(marker_rect.adjusted(1, 1, -1, -1))
        painter.end()

    def mousePressEvent(self, event):
        self._handle_mouse(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse(event)

    def _handle_mouse(self, event):
        pos = event.position()
        s = max(0.0, min(1.0, pos.x() / max(1, self.width() - 1)))
        v = 1.0 - max(0.0, min(1.0, pos.y() / max(1, self.height() - 1)))
        self.set_sv(s, v)
        self.svChanged.emit(self._saturation, self._value)


def _draw_checkerboard(painter: QPainter, rect: QRect, tile: int = 6):
    dark = QColor(110, 110, 110)
    light = QColor(160, 160, 160)
    start_x = rect.left()
    start_y = rect.top()
    for y in range(start_y, rect.bottom() + tile, tile):
        for x in range(start_x, rect.right() + tile, tile):
            color = light if ((x // tile + y // tile) % 2 == 0) else dark
            painter.fillRect(QRect(x, y, tile, tile), color)


class _AlphaSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._display_color = QColor(0, 0, 0, 255)
        self.setRange(0, 255)
        self.setMinimumHeight(18)
        self.setMaximumHeight(22)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_display_color(self, color: QColor):
        self._display_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        painter = QPainter(self)

        groove = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, option, QStyle.SubControl.SC_SliderGroove, self)
        groove = groove.adjusted(2, 2, -2, -2)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        radius = groove.height() / 2.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(groove), radius, radius)
        painter.setClipPath(path)
        _draw_checkerboard(painter, groove, tile=6)

        gradient = QLinearGradient(
            float(groove.left()),
            float(groove.center().y()),
            float(groove.right()),
            float(groove.center().y()),
        )
        start_color = QColor(self._display_color)
        start_color.setAlpha(0)
        end_color = QColor(self._display_color)
        gradient.setColorAt(0.0, start_color)
        gradient.setColorAt(1.0, end_color)
        painter.fillRect(groove, gradient)
        painter.restore()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(68, 68, 68)))
        painter.drawPath(path)
        painter.restore()

        option.subControls = QStyle.SubControl.SC_SliderHandle
        self.style().drawComplexControl(QStyle.ComplexControl.CC_Slider, option, painter, self)


class ColorPickerWidget(QWidget):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(0, 0, 0, 255)
        self._saturation = 1.0
        self._value = 1.0
        self._sv_canvas = _SVCanvas()
        self._sv_canvas.svChanged.connect(self._on_sv_changed)

        self._hue_slider = QSlider(Qt.Orientation.Horizontal)
        self._hue_slider.setRange(0, 359)
        self._hue_slider.setMinimumHeight(18)
        self._hue_slider.setMaximumHeight(22)
        self._hue_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._hue_slider.valueChanged.connect(self._on_hue_changed)
        self._hue_slider.setStyleSheet(self._build_hue_slider_stylesheet())

        self._alpha_slider = _AlphaSlider()
        self._alpha_slider.valueChanged.connect(self._on_alpha_changed)

        # Hex input removed - now handled by palette panel

        self._preview_label = QLabel()
        self._preview_label.setFixedSize(28, 28)
        self._preview_label.setStyleSheet("border: 1px solid #666; border-radius: 4px; background: transparent;")
        self._preview_label.setScaledContents(True)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("Alpha:"))
        bottom_layout.addWidget(self._alpha_slider, stretch=1)
        bottom_layout.addWidget(self._preview_label)

        # Hex input completely removed from color picker

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)  # Smaller margins
        main_layout.setSpacing(5)  # Responsive spacing
        main_layout.addWidget(self._sv_canvas, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(8)  # Reduced spacing
        main_layout.addWidget(self._hue_slider)
        main_layout.addLayout(bottom_layout)
        # Hex input now handled by palette panel

        # RESPONSIVE: Adapt to available space
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Dynamic sizing based on parent size
        self.setMinimumSize(120, 150)
        self.setMaximumSize(180, 280)  # Allow growth when space available

        self.set_color(self._color)

    def _build_hue_slider_stylesheet(self):
        return """
        QSlider::groove:horizontal {
            border: 1px solid #444;
            height: 16px;
            border-radius: 8px;
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255,0,0,255),
                stop:0.17 rgba(255,255,0,255),
                stop:0.33 rgba(0,255,0,255),
                stop:0.5 rgba(0,255,255,255),
                stop:0.66 rgba(0,0,255,255),
                stop:0.83 rgba(255,0,255,255),
                stop:1 rgba(255,0,0,255));
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #222;
            width: 12px;
            margin: 0 -2px;
            border-radius: 6px;
        }
        """

    def set_color(self, color: QColor, emit_signal: bool = False):
        color = QColor(color)
        self._color = color
        h, s, v, _ = color.getHsv()
        if h == -1:
            h = self._hue_slider.value()
        self._saturation = s / 255.0
        self._value = v / 255.0
        self._sv_canvas.set_sv(self._saturation, self._value)
        self._hue_slider.blockSignals(True)
        self._hue_slider.setValue(h % 360)
        self._hue_slider.blockSignals(False)
        self._sv_canvas.set_hue(h % 360)
        self._alpha_slider.blockSignals(True)
        self._alpha_slider.setValue(color.alpha())
        self._alpha_slider.blockSignals(False)
        self._alpha_slider.set_display_color(color)
        self._update_preview(color)
        # Hex input now handled by palette panel
        if emit_signal:
            self.colorChanged.emit(color)

    def current_color(self) -> QColor:
        return QColor(self._color)

    def _compose_color(self):
        color = QColor()
        color.setHsvF(self._hue_slider.value() / 360.0, self._saturation, self._value, self._alpha_slider.value() / 255.0)
        return color

    def _on_sv_changed(self, s: float, v: float):
        self._saturation = s
        self._value = v
        self._update_color_from_inputs()

    def _on_hue_changed(self, value: int):
        self._sv_canvas.set_hue(value)
        self._update_color_from_inputs()

    def _on_alpha_changed(self, value: int):
        self._update_color_from_inputs()

    def _update_color_from_inputs(self):
        color = self._compose_color()
        self._color = color
        self._update_preview(color)
        # Hex input now handled by palette panel
        self.colorChanged.emit(color)

    def _update_preview(self, color: QColor | None = None):
        if color is None:
            color = self._color
        size = self._preview_label.size()
        width = max(1, size.width())
        height = max(1, size.height())
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        _draw_checkerboard(painter, pixmap.rect(), tile=4)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        self._preview_label.setPixmap(pixmap)
        self._alpha_slider.set_display_color(color)
"""Steam Play Hours Simulator
=================================
An application you can launch instead of (or alongside) a Steam game so the
game's entry still accumulates play hours while the actual heavy executable
gets to rest. Useful for:
	* Rebuilding hours after moving a title to another store (Epic, GOG, etc.)
	* Preserving hardware / energy by not running the real game process
	* Keeping a minimalist window open just to track elapsed time (DD:HH:MM:SS)

It does not spoof processes, inject, or communicate over the network; it simply
shows a continuously advancing timer. Add it as a Non‑Steam Game to your library.

DISCLAIMER: Intentionally inflating playtime may violate platform Terms of
Service or community expectations. Use responsibly. This tool only displays
local time progression.

Quick usage:
	python main.py --offset-hours 5.5
	python main.py --offset-seconds 3600

Build to EXE:
	pyinstaller --noconfirm --onefile --windowed --name "Steam Play Hours Simulator" main.py
"""

from __future__ import annotations

import sys
import time
from argparse import ArgumentParser

try:
	from PySide6.QtCore import Qt, QTimer
	from PySide6.QtGui import QFont, QPalette, QColor, QAction
	from PySide6.QtWidgets import (
		QApplication,
		QLabel,
		QMainWindow,
		QWidget,
		QVBoxLayout,
		QHBoxLayout,
		QPushButton,
		QMenu,
		QMessageBox,
	)
except ImportError as e:  # Graceful message if dependency missing
	print("PySide6 is not installed. Install dependencies with: pip install -r requirements.txt", file=sys.stderr)
	raise


APP_TITLE = "Steam Play Hours Simulator"


def parse_args():
	parser = ArgumentParser(description=APP_TITLE)
	parser.add_argument("--offset-seconds", type=int, default=0, help="Pretend the timer already ran this many seconds.")
	parser.add_argument("--offset-hours", type=float, default=0.0, help="Pretend the timer already ran this many hours (adds to offset-seconds).")
	parser.add_argument("--compact", action="store_true", help="Use a more compact window size.")
	parser.add_argument("--no-accent-pulse", action="store_true", help="Disable subtle accent color pulsing animation.")
	return parser.parse_args()


def format_duration(seconds: int) -> str:
	days, rem = divmod(seconds, 86400)
	hours, rem = divmod(rem, 3600)
	minutes, secs = divmod(rem, 60)
	return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"


class MainWindow(QMainWindow):
	def __init__(self, start_epoch: float, accent_pulse: bool = True, compact: bool = False):
		super().__init__()
		self.start_epoch = start_epoch
		self.accent_pulse = accent_pulse
		self._pulse_direction = 1
		self._pulse_value = 0
		self.setWindowTitle(APP_TITLE)
		self.setMinimumWidth(520 if not compact else 400)
		self.setMinimumHeight(260 if not compact else 180)
		self._build_ui(compact)
		self._apply_styles()
		self._init_timers()

	# UI Construction -------------------------------------------------
	def _build_ui(self, compact: bool):
		central = QWidget()
		main_layout = QVBoxLayout()
		main_layout.setContentsMargins(28, 24, 28, 16)
		main_layout.setSpacing(12)

		# Grid-like horizontal layout for time units
		units_row = QHBoxLayout()
		units_row.setSpacing(10)

		big_font = QFont("Segoe UI", 50 if not compact else 38, QFont.Bold)
		caption_font = QFont("Segoe UI", 11 if not compact else 10, QFont.Medium)

		self._number_labels = []  # For pulse + updates

		def make_unit(title: str) -> QLabel:
			wrapper = QVBoxLayout()
			wrapper.setSpacing(2)
			cap = QLabel(title)
			cap.setAlignment(Qt.AlignCenter)
			cap.setFont(caption_font)
			cap.setObjectName("CaptionLabel")
			num = QLabel("00")
			num.setAlignment(Qt.AlignCenter)
			num.setFont(big_font)
			num.setObjectName("NumberLabel")
			self._number_labels.append(num)
			wrapper.addWidget(cap)
			wrapper.addWidget(num)
			container = QWidget()
			container.setLayout(wrapper)
			units_row.addWidget(container, 1)
			return num

		self.days_label = make_unit("DAYS")
		self.hours_label = make_unit("HOURS")
		self.minutes_label = make_unit("MINUTES")
		self.seconds_label = make_unit("SECONDS")

		main_layout.addLayout(units_row)

		# Control buttons row
		btn_row = QHBoxLayout()
		btn_row.setSpacing(8)
		btn_row.addStretch(1)

		self.reset_btn = QPushButton("Reset (R)")
		self.reset_btn.clicked.connect(self.confirm_reset)
		self.reset_btn.setCursor(Qt.PointingHandCursor)
		btn_row.addWidget(self.reset_btn)

		self.always_on_top_btn = QPushButton("Stay On Top")
		self.always_on_top_btn.setCheckable(True)
		self.always_on_top_btn.clicked.connect(self.toggle_on_top)
		self.always_on_top_btn.setCursor(Qt.PointingHandCursor)
		btn_row.addWidget(self.always_on_top_btn)

		info_btn = QPushButton("About")
		info_btn.clicked.connect(self.show_about)
		info_btn.setCursor(Qt.PointingHandCursor)
		btn_row.addWidget(info_btn)

		main_layout.addLayout(btn_row)

		central.setLayout(main_layout)
		self.setCentralWidget(central)

		# Shortcuts
		self.reset_action = QAction("Reset", self)
		self.reset_action.setShortcut("R")
		self.reset_action.triggered.connect(self.confirm_reset)
		self.addAction(self.reset_action)

	# Styling ----------------------------------------------------------
	def _apply_styles(self):
		# Dark palette
		palette = QPalette()
		base = QColor(18, 18, 20)
		panel = QColor(28, 28, 32)
		text = QColor(235, 235, 237)
		accent = QColor(52, 152, 219)
		palette.setColor(QPalette.Window, base)
		palette.setColor(QPalette.Base, base)
		palette.setColor(QPalette.AlternateBase, panel)
		palette.setColor(QPalette.WindowText, text)
		palette.setColor(QPalette.Text, text)
		palette.setColor(QPalette.Button, panel)
		palette.setColor(QPalette.ButtonText, text)
		palette.setColor(QPalette.Highlight, accent)
		palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
		self.setPalette(palette)

		self.setStyleSheet(
			"""
			QMainWindow { background: #121214; }
			QLabel#NumberLabel { color: #FFFFFF; letter-spacing: 2px; }
			QLabel#CaptionLabel { color: #8b9199; font-size: 11px; letter-spacing: 1px; }
			QPushButton { background: #1c1f24; color: #e2e5e9; padding: 8px 14px; border: 1px solid #2c313a; border-radius: 6px; font-size: 14px; }
			QPushButton:hover { background: #2a2f35; }
			QPushButton:pressed { background: #23272d; }
			QPushButton:checked { background: #347edb; border-color: #347edb; color: white; }
			QPushButton:focus { outline: none; border: 1px solid #347edb; }
			"""
		)

	# Timers -----------------------------------------------------------
	def _init_timers(self):
		# Main update timer
		self.update_timer = QTimer(self)
		self.update_timer.timeout.connect(self._update)
		self.update_timer.start(1000)

		# Accent pulse timer (subtle)
		if self.accent_pulse:
			self.pulse_timer = QTimer(self)
			self.pulse_timer.timeout.connect(self._pulse)
			self.pulse_timer.start(120)
		else:
			self.pulse_timer = None

	# Core Update ------------------------------------------------------
	def _update(self):
		elapsed = int(time.time() - self.start_epoch)
		days, rem = divmod(elapsed, 86400)
		hours, rem = divmod(rem, 3600)
		minutes, secs = divmod(rem, 60)
		self.days_label.setText(f"{days:02d}")
		self.hours_label.setText(f"{hours:02d}")
		self.minutes_label.setText(f"{minutes:02d}")
		self.seconds_label.setText(f"{secs:02d}")
		self.setWindowTitle(f"{APP_TITLE}  |  {days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}")

	# Pulse effect -----------------------------------------------------
	def _pulse(self):
		# Animate a slight accent glow across all number labels.
		self._pulse_value += self._pulse_direction
		if self._pulse_value >= 40:
			self._pulse_direction = -1
		elif self._pulse_value <= 0:
			self._pulse_direction = 1
		base = 255
		blue = 255 - self._pulse_value
		color = f"rgb({base},{base},{blue})"
		for lbl in self._number_labels:
			lbl.setStyleSheet(f"color: {color}; letter-spacing: 2px;")

	# Actions ----------------------------------------------------------
	def confirm_reset(self):
		resp = QMessageBox.question(
			self,
			"Reset Timer",
			"Reset elapsed time to 0? This doesn't affect any stored data (none is stored).",
			QMessageBox.Yes | QMessageBox.No,
			QMessageBox.No,
		)
		if resp == QMessageBox.Yes:
			self.start_epoch = time.time()
			self._update()

	def toggle_on_top(self):
		if self.always_on_top_btn.isChecked():
			self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
			self.always_on_top_btn.setText("On Top ✓")
		else:
			self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
			self.always_on_top_btn.setText("Stay On Top")
		self.show()  # Re-apply flags

	def show_about(self):
		QMessageBox.information(
			self,
			"About",
			(
				f"{APP_TITLE}\n\n"
				"A lightweight placeholder you can run instead of a game so Steam \n"
				"continues counting playtime. Displays an on-going DD:HH:MM:SS timer.\n\n"
				"Created for CodeKokeshi.\n"
				"GitHub: https://github.com/CodeKokeshi/\n"
				"itch.io: https://codekokeshi.itch.io/\n\n"
				"No networking, no injection, no data collection—just a clock.\n"
				"Please respect platform Terms of Service."
			),
		)


def main():
	args = parse_args()
	offset_total = args.offset_seconds + int(args.offset_hours * 3600)
	# Start epoch goes backwards by offset for display
	start_epoch = time.time() - offset_total

	app = QApplication(sys.argv)
	app.setApplicationName(APP_TITLE)
	window = MainWindow(start_epoch=start_epoch, accent_pulse=not args.no_accent_pulse, compact=args.compact)
	window.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()


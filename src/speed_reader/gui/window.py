"""
Speed Reader GUI Window
Main window for the speed reader application.
"""
import sys
import os
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSlider, QSpinBox, QTextEdit,
    QGroupBox, QProgressBar, QMessageBox, QCheckBox, QComboBox, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont, QResizeEvent
from ..parsers.file_parser import FileParser
from ..models.document import DocumentMetadata
from ..tts.manager import TTSManager
from ..utils.file_history import FileHistory
from .styles import get_stylesheet


class SpeedReaderWindow(QMainWindow):
    """Main window for the speed reader application."""
    
    def __init__(self):
        super().__init__()
        self.metadata: Optional[DocumentMetadata] = None
        self.current_index: int = 0
        self.is_playing: bool = False
        self.timer: Optional[QTimer] = None
        self.file_path: Optional[str] = None
        self.tts = TTSManager()
        self.file_history = FileHistory()
        
        # Load saved speed preference
        self.wpm: int = self.file_history.get_speed()
        
        # Fullscreen state
        self.is_fullscreen: bool = False
        self.fullscreen_widget: Optional[QWidget] = None
        
        self.init_ui()
        self.setup_timer()
        self.update_recent_files()  # Initialize recent files dropdown
        self.load_last_file()  # Ask to load last file
        self.update_font_sizes()  # Set initial font size
        self.validate_tts_controls()  # Validate TTS controls based on WPM
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize to scale fonts."""
        super().resizeEvent(event)
        self.update_font_sizes()
    
    def update_font_sizes(self):
        """Update font sizes based on window size."""
        height = self.height()
        
        # Scale font size based on window height with better proportions
        # Base size of 36px, scale up for larger windows
        base_size = 36
        scale_factor = min(4.0, height / 400.0)  # Scale up to 4x for tall windows (144px max)
        font_size = int(base_size * scale_factor)
        
        # Ensure reasonable bounds - increased maximum
        font_size = max(24, min(144, font_size))
        
        # Update the stylesheet with the new font size
        self.word_label.setStyleSheet(f"""
            QLabel {{
                font-size: {font_size}px;
                font-weight: 600;
                padding: 15px 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1e1e1e);
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                letter-spacing: 1px;
                min-height: 60px;
            }}
        """)
        
        # Also scale fullscreen font if in fullscreen
        if self.is_fullscreen and hasattr(self, 'fullscreen_word_label'):
            fs_font_size = max(48, min(200, self.height() // 4))  # More aggressive scaling for fullscreen
            fs_stylesheet = f"""
                QLabel {{
                    color: #ffffff;
                    background-color: #000000;
                    padding: 10px 0px;
                    font-size: {fs_font_size}px;
                    font-weight: bold;
                }}
            """
            self.fullscreen_word_label.setStyleSheet(fs_stylesheet)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Speed Reader")
        self.setGeometry(100, 100, 1000, 700)  # Slightly smaller default size
        self.setMinimumSize(700, 500)  # More reasonable minimum size for smaller screens
        
        # Apply modern stylesheet
        self.setStyleSheet(get_stylesheet('dark'))
        
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(6)  # Reduced spacing between groups
        layout.setContentsMargins(8, 8, 8, 8)  # Add some margins
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(6, 6, 6, 6)  # Reduce margins
        file_layout.setSpacing(4)  # Reduce spacing
        
        file_button_layout = QHBoxLayout()
        self.file_label = QLabel("No file loaded")
        self.file_label.setWordWrap(True)
        self.load_file_btn = QPushButton("Load File")
        self.load_file_btn.clicked.connect(self.load_file)
        self.paste_text_btn = QPushButton("Paste Text")
        self.paste_text_btn.clicked.connect(self.paste_text)
        
        file_button_layout.addWidget(self.load_file_btn)
        file_button_layout.addWidget(self.paste_text_btn)
        file_layout.addWidget(self.file_label)
        file_layout.addLayout(file_button_layout)
        
        # Recent files dropdown
        recent_layout = QHBoxLayout()
        recent_layout.addWidget(QLabel("Recent Files:"))
        self.recent_files_combo = QComboBox()
        self.recent_files_combo.setMinimumWidth(400)
        self.recent_files_combo.setEnabled(False)
        self.recent_files_combo.currentTextChanged.connect(self.on_recent_file_selected)
        recent_layout.addWidget(self.recent_files_combo)
        recent_layout.addStretch()
        file_layout.addLayout(recent_layout)
        
        file_group.setLayout(file_layout)
        
        # Enhanced Starting position group
        position_group = QGroupBox("Starting Position & Context")
        position_layout = QVBoxLayout()
        position_layout.setContentsMargins(6, 6, 6, 6)  # Reduce margins
        position_layout.setSpacing(4)  # Reduce spacing
        
        # Position info display (page, chapter, percentage)
        info_layout = QHBoxLayout()
        self.page_label = QLabel("Page: -")
        self.page_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #b0b0b0;")
        self.chapter_label = QLabel("Chapter: -")
        self.chapter_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #b0b0b0;")
        self.percentage_label = QLabel("Progress: 0%")
        self.percentage_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #b0b0b0;")
        
        info_layout.addWidget(self.page_label)
        info_layout.addWidget(self.chapter_label)
        info_layout.addWidget(self.percentage_label)
        info_layout.addStretch()
        position_layout.addLayout(info_layout)
        
        # Chapter navigation dropdown
        chapter_nav_layout = QHBoxLayout()
        chapter_nav_layout.addWidget(QLabel("Jump to Chapter:"))
        self.chapter_combo = QComboBox()
        self.chapter_combo.setEnabled(False)
        self.chapter_combo.setMinimumWidth(400)  # Make dropdown wider
        self.chapter_combo.setEditable(False)  # Make it searchable/dropdown
        self.chapter_combo.setMaxVisibleItems(20)  # Show more items in dropdown
        self.chapter_combo.currentIndexChanged.connect(self.on_chapter_selected)
        # Add tooltip support for full chapter names
        self.chapter_combo.setToolTip("Select a chapter to jump to")
        chapter_nav_layout.addWidget(self.chapter_combo)
        chapter_nav_layout.addStretch()
        position_layout.addLayout(chapter_nav_layout)
        
        # Position slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Position:"))
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setMinimum(0)
        self.position_slider.setMaximum(0)
        self.position_slider.valueChanged.connect(self.on_position_changed)
        slider_layout.addWidget(self.position_slider)
        position_layout.addLayout(slider_layout)
        
        # Context preview (shows surrounding text)
        context_label = QLabel("Context Preview:")
        context_label.setStyleSheet("font-weight: bold;")
        position_layout.addWidget(context_label)
        
        self.context_preview = QTextEdit()
        self.context_preview.setReadOnly(True)
        self.context_preview.setMinimumHeight(80)  # More flexible minimum height
        self.context_preview.setMaximumHeight(150)  # More flexible maximum height
        self.context_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.context_preview.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 6px;
                font-size: 10px;
                line-height: 1.4;
            }
        """)
        position_layout.addWidget(self.context_preview)
        
        position_group.setLayout(position_layout)
        
        # Word display area
        display_group = QGroupBox("Reading Display")
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(4, 4, 4, 4)  # Reduce margins
        
        self.word_label = QLabel("Load a file to begin reading")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.word_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                padding: 15px 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1e1e1e);
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                letter-spacing: 1px;
                min-height: 60px;
            }
        """)
        display_layout.addWidget(self.word_label, stretch=1)  # Allow stretching
        display_group.setLayout(display_layout)
        
        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(6, 6, 6, 6)  # Reduce margins
        controls_layout.setSpacing(6)  # Reduce spacing
        
        # WPM and TTS controls
        top_controls = QHBoxLayout()
        
        wpm_layout = QHBoxLayout()
        wpm_layout.addWidget(QLabel("WPM:"))
        self.wpm_spinbox = QSpinBox()
        self.wpm_spinbox.setMinimum(50)
        self.wpm_spinbox.setMaximum(1000)
        self.wpm_spinbox.setValue(self.wpm)
        self.wpm_spinbox.setFixedWidth(80)  # Fixed width to prevent cutoff
        self.wpm_spinbox.valueChanged.connect(self.on_wpm_changed)
        wpm_layout.addWidget(self.wpm_spinbox)
        
        # Add speed preset dropdown
        wpm_layout.addWidget(QLabel("Presets:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["50", "75", "100", "125", "150", "175", "192", "250", "300", "350", "400", "500", "600", "700", "800", "900", "1000"])
        self.speed_combo.setCurrentText(str(self.wpm))  # Set to loaded speed
        self.speed_combo.setFixedWidth(60)
        self.speed_combo.currentTextChanged.connect(self.on_speed_preset_changed)
        wpm_layout.addWidget(self.speed_combo)
        
        # TTS checkbox
        self.tts_checkbox = QCheckBox("TTS")
        self.tts_checkbox.setEnabled(self.tts.is_available())
        if not self.tts.is_available():
            self.tts_checkbox.setToolTip("TTS not available on this system")
        self.tts_checkbox.stateChanged.connect(self.on_tts_toggled)
        
        top_controls.addLayout(wpm_layout)
        top_controls.addStretch()
        top_controls.addWidget(self.tts_checkbox)
        controls_layout.addLayout(top_controls)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setEnabled(False)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_position)
        self.reset_btn.setEnabled(False)
        
        self.prev_word_btn = QPushButton("← Previous")
        self.prev_word_btn.clicked.connect(self.previous_word)
        self.prev_word_btn.setEnabled(False)
        
        self.next_word_btn = QPushButton("Next →")
        self.next_word_btn.clicked.connect(self.next_word)
        self.next_word_btn.setEnabled(False)
        
        self.fullscreen_btn = QPushButton("⛶ Fullscreen")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setEnabled(False)
        
        button_layout.addWidget(self.prev_word_btn)
        button_layout.addWidget(self.play_pause_btn)
        button_layout.addWidget(self.next_word_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.fullscreen_btn)
        controls_layout.addLayout(button_layout)
        
        controls_group.setLayout(controls_layout)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_label = QLabel("0 / 0 words")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        # Assemble main layout
        layout.addWidget(file_group)
        layout.addWidget(position_group)
        layout.addWidget(display_group, stretch=2)  # Give more stretch to display
        layout.addWidget(controls_group)
        layout.addLayout(progress_layout)
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Load File', self.load_file)
        file_menu.addAction('Paste Text', self.paste_text)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # View menu
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Fullscreen', self.toggle_fullscreen)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Speed Reader", 
                         "Speed Reader v1.0\n\nA fast text reading application with TTS support.")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        QShortcut(QKeySequence("Space"), self, self.toggle_play_pause)
        QShortcut(QKeySequence("Left"), self, self.previous_word)
        QShortcut(QKeySequence("Right"), self, self.next_word)
        QShortcut(QKeySequence("R"), self, self.reset_position)
        QShortcut(QKeySequence("Ctrl+F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Escape"), self, self.exit_fullscreen)
    
    def setup_timer(self):
        """Setup the timer for word display."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_next_word)
    
    def validate_tts_controls(self):
        """Validate TTS controls based on current WPM."""
        if self.wpm > 192:
            self.tts_checkbox.setEnabled(False)
            if self.tts.enabled:
                self.tts_checkbox.setChecked(False)
                self.on_tts_toggled(False)
        else:
            self.tts_checkbox.setEnabled(True)
    
    def load_file(self):
        """Load a file using file dialog."""
        # Start from last file's directory if available
        last_file = self.file_history.get_last_file()
        start_dir = os.path.dirname(last_file) if last_file and os.path.exists(last_file) else ""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            start_dir,
            "All Supported (*.pdf *.epub *.docx *.doc *.txt);;PDF (*.pdf);;EPUB (*.epub);;Word (*.docx *.doc);;Text (*.txt)"
        )
        
        if file_path:
            self.parse_file(file_path)
    
    def paste_text(self):
        """Paste text from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if text:
            self.metadata = FileParser.parse_text(text)
            self.file_path = None
            self.file_label.setText("Text pasted from clipboard")
            self.initialize_reading()
        else:
            QMessageBox.warning(self, "No Text", "Clipboard is empty or doesn't contain text.")
    
    def parse_file(self, file_path: str):
        """Parse the selected file."""
        self.file_path = file_path
        self.file_label.setText(f"Loading: {os.path.basename(file_path)}...")
        QApplication.processEvents()  # Update UI
        
        try:
            metadata = FileParser.parse_file(file_path)
            
            if metadata and len(metadata.words) > 0:
                self.metadata = metadata
                self.file_path = file_path
                self.file_label.setText(f"Loaded: {os.path.basename(file_path)} ({len(metadata.words)} words)")
                
                # Add to file history
                self.file_history.add_file(file_path)
                self.update_recent_files()
                
                self.initialize_reading()
            else:
                # More detailed error message
                file_ext = os.path.splitext(file_path)[1].lower()
                error_msg = f"Failed to parse file or file is empty.\n\n"
                error_msg += f"File: {file_path}\n"
                error_msg += f"Type: {file_ext}\n\n"
                
                if file_ext == '.epub':
                    error_msg += "Possible issues:\n"
                    error_msg += "- EPUB file may be corrupted\n"
                    error_msg += "- File may be encrypted or DRM-protected\n"
                    error_msg += "- File may contain only images (no text)\n"
                    error_msg += "\nCheck the console for detailed error messages."
                
                QMessageBox.critical(self, "Error", error_msg)
                self.file_label.setText("No file loaded")
        except Exception as e:
            error_msg = f"Error loading file:\n\n{str(e)}\n\nFile: {file_path}"
            QMessageBox.critical(self, "Error", error_msg)
            self.file_label.setText("No file loaded")
            import traceback
            traceback.print_exc()
    
    def initialize_reading(self):
        """Initialize reading state after loading file."""
        if not self.metadata or not self.metadata.words:
            return
        
        # Try to load saved position
        saved_position = self.file_history.get_position(self.file_path)
        if saved_position is not None and 0 <= saved_position < len(self.metadata.words):
            reply = QMessageBox.question(
                self,
                "Resume Reading?",
                f"Found saved position at word {saved_position + 1}.\n\nResume from saved position?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.current_index = saved_position
            else:
                self.current_index = 0
        else:
            self.current_index = 0
        
        self.position_slider.setMaximum(len(self.metadata.words) - 1)
        self.progress_bar.setMaximum(len(self.metadata.words) - 1)
        
        self.play_pause_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.prev_word_btn.setEnabled(True)
        self.next_word_btn.setEnabled(True)
        self.fullscreen_btn.setEnabled(True)
        
        # Populate chapter combo box
        self.populate_chapters()
        
        self.update_display()
        self.update_progress()
        self.update_position_info()
        self.update_position_controls()
    
    def populate_chapters(self):
        """Populate the chapter dropdown with available chapters."""
        self.chapter_combo.blockSignals(True)
        self.chapter_combo.clear()
        
        if not self.metadata or not self.metadata.chapter_names:
            self.chapter_combo.setEnabled(False)
            self.chapter_combo.blockSignals(False)
            return
        
        # Add chapters to combo box with full names
        for chapter_name in self.metadata.chapter_names:
            # Add item with full name (no truncation)
            self.chapter_combo.addItem(chapter_name)
            # Set tooltip for each item to show full name
            index = self.chapter_combo.count() - 1
            self.chapter_combo.setItemData(index, chapter_name, Qt.ItemDataRole.ToolTipRole)
        
        self.chapter_combo.setEnabled(True)
        self.chapter_combo.blockSignals(False)
    
    def on_chapter_selected(self, index: int):
        """Handle chapter selection from dropdown."""
        if not self.metadata or index < 0:
            return
        
        # Find the first word index for this chapter
        chapter_name = self.metadata.chapter_names[index]
        
        # Search for the first occurrence of this chapter
        for word_idx in range(len(self.metadata.words)):
            if self.metadata.word_to_chapter.get(word_idx) == chapter_name:
                self.current_index = word_idx
                self.update_display()
                self.update_progress()
                self.update_position_info()
                self.update_position_controls()
                break
    
    def on_position_changed(self, value: int):
        """Handle position slider change."""
        if value != self.current_index:
            self.current_index = value
            self.update_display()
            self.update_progress()
            self.update_position_info()
    
    def on_wpm_changed(self, value: int):
        """Handle WPM change."""
        self.wpm = value
        
        # Disable TTS if WPM > 192 (pyttsx3 Windows SAPI limitation)
        if value > 192:
            self.tts_checkbox.setEnabled(False)
            if self.tts.enabled:
                self.tts_checkbox.setChecked(False)
                self.on_tts_toggled(False)
        else:
            self.tts_checkbox.setEnabled(True)
        
        self.tts.set_wpm(value)
        if self.is_playing:
            self.start_reading()
        # Save speed preference
        self.file_history.save_speed(value)
        # Update speed combo to match current value
        if hasattr(self, 'speed_combo'):
            current_text = str(value)
            if self.speed_combo.findText(current_text) == -1:
                # Add the custom speed to the combo temporarily
                self.speed_combo.addItem(current_text)
            self.speed_combo.setCurrentText(current_text)
    
    def on_speed_preset_changed(self, text: str):
        """Handle speed preset selection."""
        try:
            speed = int(text)
            self.wpm_spinbox.setValue(speed)
        except ValueError:
            pass
    
    def on_tts_toggled(self, state: int):
        """Handle TTS checkbox toggle."""
        enabled = state == Qt.CheckState.Checked.value or state == 2
        self.tts.set_enabled(enabled)
    
    def toggle_play_pause(self):
        """Toggle play/pause state."""
        if not self.metadata or not self.metadata.words:
            return
        
        if self.is_playing:
            self.pause_reading()
        else:
            self.start_reading()
    
    def start_reading(self):
        """Start reading."""
        if not self.metadata or not self.metadata.words or self.current_index >= len(self.metadata.words):
            return
        
        self.is_playing = True
        self.play_pause_btn.setText("Pause")
        
        # Disable WPM controls only if TTS is enabled
        if self.tts.enabled:
            self.wpm_spinbox.setEnabled(False)
            self.speed_combo.setEnabled(False)
            self.tts_checkbox.setEnabled(False)
            
            # Queue all remaining words to be spoken asynchronously
            remaining_words = self.metadata.words[self.current_index:]
            full_text = ' '.join(remaining_words)
            self.tts.speak(full_text)
        else:
            # If not using TTS, disable TTS checkbox
            self.tts_checkbox.setEnabled(False)
        
        # Calculate interval in milliseconds (60 seconds / wpm * 1000)
        interval = int((60.0 / self.wpm) * 1000)
        self.timer.start(interval)
    
    def pause_reading(self):
        """Pause reading."""
        self.is_playing = False
        self.play_pause_btn.setText("Play")
        if self.timer:
            self.timer.stop()
        self.tts.stop()
        
        # Re-enable all controls
        self.wpm_spinbox.setEnabled(True)
        self.speed_combo.setEnabled(True)
        self.tts_checkbox.setEnabled(True)
    
    def show_next_word(self):
        """Show the next word (called by timer)."""
        if not self.metadata or self.current_index >= len(self.metadata.words) - 1:
            self.pause_reading()
            if self.current_index >= len(self.metadata.words) - 1:
                QMessageBox.information(self, "Finished", "You've reached the end of the document!")
            return
        
        self.current_index += 1
        self.update_display()
        self.update_progress()
        self.update_position_info()
        
        # Save position periodically (every 10 words)
        if self.file_path and self.current_index % 10 == 0:
            self.file_history.save_position(self.file_path, self.current_index)
        
        # Update position slider without triggering events
        self.position_slider.blockSignals(True)
        self.position_slider.setValue(self.current_index)
        self.position_slider.blockSignals(False)
    
    def next_word(self):
        """Move to next word manually."""
        if not self.metadata or self.current_index >= len(self.metadata.words) - 1:
            return
        
        self.current_index += 1
        self.update_display()
        self.update_progress()
        self.update_position_info()
        self.update_position_controls()
    
    def previous_word(self):
        """Move to previous word manually."""
        if not self.metadata or self.current_index <= 0:
            return
        
        self.current_index -= 1
        self.update_display()
        self.update_progress()
        self.update_position_info()
        self.update_position_controls()
    
    def reset_position(self):
        """Reset to beginning."""
        self.pause_reading()
        self.current_index = 0
        self.update_display()
        self.update_progress()
        self.update_position_info()
        self.update_position_controls()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode."""
        if not self.metadata or not self.metadata.words:
            return
        
        self.is_fullscreen = True
        
        # Create fullscreen widget
        self.fullscreen_widget = QWidget()
        self.fullscreen_widget.setStyleSheet("background-color: #000000;")
        fullscreen_layout = QVBoxLayout(self.fullscreen_widget)
        fullscreen_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a horizontal layout for the three words
        words_layout = QHBoxLayout()
        words_layout.setSpacing(30)  # Reduced spacing between words
        words_layout.setContentsMargins(30, 0, 30, 0)  # Reduced margins
        
        # Previous word label
        self.prev_word_label = QLabel()
        prev_font = QFont()
        prev_font.setPointSize(48)  # Smaller than current word
        prev_font.setWeight(QFont.Weight.Normal)
        self.prev_word_label.setFont(prev_font)
        self.prev_word_label.setStyleSheet("color: #666666; background-color: #000000;")
        self.prev_word_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.prev_word_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Current word label (main focus)
        self.fullscreen_word_label = QLabel()
        self.fullscreen_word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Make the font responsive for fullscreen
        font = QFont()
        font.setPointSize(96)  # Large but not as huge for better responsiveness
        font.setWeight(QFont.Weight.Bold)
        self.fullscreen_word_label.setFont(font)
        self.fullscreen_word_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #000000;
                padding: 10px 0px;
                min-height: 80px;
            }
        """)
        self.fullscreen_word_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Next word label
        self.next_word_label = QLabel()
        next_font = QFont()
        next_font.setPointSize(48)  # Smaller than current word
        next_font.setWeight(QFont.Weight.Normal)
        self.next_word_label.setFont(next_font)
        self.next_word_label.setStyleSheet("color: #666666; background-color: #000000;")
        self.next_word_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.next_word_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Add words to horizontal layout
        words_layout.addWidget(self.prev_word_label, stretch=1)
        words_layout.addWidget(self.fullscreen_word_label, stretch=2)
        words_layout.addWidget(self.next_word_label, stretch=1)
        
        # Exit button (small, top-right corner)
        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(50, 50)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """)
        exit_btn.clicked.connect(self.exit_fullscreen)
        
        # Layout for fullscreen
        fullscreen_layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        fullscreen_layout.addStretch()
        fullscreen_layout.addLayout(words_layout)
        fullscreen_layout.addStretch()
        
        # Set up shortcuts on the fullscreen widget
        QShortcut(QKeySequence("Escape"), self.fullscreen_widget, self.exit_fullscreen)
        QShortcut(QKeySequence("Space"), self.fullscreen_widget, self.toggle_play_pause)
        QShortcut(QKeySequence("Left"), self.fullscreen_widget, self.previous_word)
        QShortcut(QKeySequence("Right"), self.fullscreen_widget, self.next_word)
        QShortcut(QKeySequence("R"), self.fullscreen_widget, self.reset_position)
        
        # Show fullscreen
        self.fullscreen_widget.showFullScreen()
        
        # Update the word display
        self.update_fullscreen_display()
        
        # Hide main window
        self.hide()
    
    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if not self.is_fullscreen:
            return
        
        self.is_fullscreen = False
        
        # Hide fullscreen widget
        if self.fullscreen_widget:
            self.fullscreen_widget.hide()
            self.fullscreen_widget = None
        
        # Show main window
        self.show()
        self.activateWindow()
    
    def update_fullscreen_display(self):
        """Update the fullscreen word display."""
        if not self.is_fullscreen or not self.fullscreen_widget:
            return
        
        if not self.metadata or not self.metadata.words:
            self.prev_word_label.setText("")
            self.fullscreen_word_label.setText("No words available")
            self.next_word_label.setText("")
            return
        
        # Previous word
        if self.current_index > 0:
            prev_word = self.metadata.words[self.current_index - 1]
            self.prev_word_label.setText(prev_word)
        else:
            self.prev_word_label.setText("")
        
        # Current word
        if 0 <= self.current_index < len(self.metadata.words):
            word = self.metadata.words[self.current_index]
            self.fullscreen_word_label.setText(word)
        else:
            self.fullscreen_word_label.setText("No words available")
        
        # Next word
        if self.current_index < len(self.metadata.words) - 1:
            next_word = self.metadata.words[self.current_index + 1]
            self.next_word_label.setText(next_word)
        else:
            self.next_word_label.setText("")
    
    def update_position_controls(self):
        """Update position slider."""
        self.position_slider.blockSignals(True)
        self.position_slider.setValue(self.current_index)
        self.position_slider.blockSignals(False)
    
    def update_position_info(self):
        """Update position information (page, chapter, percentage, context)."""
        if not self.metadata:
            return
        
        # Update page info
        page_num = self.metadata.word_to_page.get(self.current_index, 1)
        total_pages = self.metadata.page_count
        self.page_label.setText(f"Page: {page_num} / {total_pages}")
        
        # Update chapter info
        chapter = self.metadata.word_to_chapter.get(self.current_index, "")
        if chapter:
            self.chapter_label.setText(f"Chapter: {chapter}")
        else:
            self.chapter_label.setText("Chapter: -")
        
        # Update percentage
        total = len(self.metadata.words)
        percentage = int((self.current_index / total) * 100) if total > 0 else 0
        self.percentage_label.setText(f"Progress: {percentage}%")
        
        # Update context preview (show surrounding words - more words for better context)
        context_words = 100  # Show 50 words before and after for more context
        start_idx = max(0, self.current_index - context_words // 2)
        end_idx = min(total, self.current_index + context_words // 2)
        
        context_text = ""
        for i in range(start_idx, end_idx):
            if i == self.current_index:
                # Highlight current word with modern styling
                context_text += f"<span style='background-color: #4a9eff; color: #ffffff; font-weight: bold; padding: 3px 6px; border-radius: 4px;'>{self.metadata.words[i]}</span> "
            else:
                context_text += f"<span style='color: #b0b0b0;'>{self.metadata.words[i]}</span> "
        
        # Wrap in HTML with proper styling
        html_content = f"""
        <div style='font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.8; color: #ffffff; padding: 4px;'>
            {context_text.strip()}
        </div>
        """
        self.context_preview.setHtml(html_content)
        
        # Update chapter combo box selection
        current_chapter = self.metadata.word_to_chapter.get(self.current_index, "")
        if current_chapter and current_chapter in self.metadata.chapter_names:
            chapter_index = self.metadata.chapter_names.index(current_chapter)
            self.chapter_combo.blockSignals(True)
            self.chapter_combo.setCurrentIndex(chapter_index)
            self.chapter_combo.blockSignals(False)
    
    def update_display(self):
        """Update the word display."""
        if not self.metadata or not self.metadata.words:
            self.word_label.setText("No words available")
            if self.is_fullscreen:
                self.update_fullscreen_display()
            return
        
        if 0 <= self.current_index < len(self.metadata.words):
            word = self.metadata.words[self.current_index]
            self.word_label.setText(word)
                
            # Update fullscreen display if active
            if self.is_fullscreen:
                self.update_fullscreen_display()
        else:
            self.word_label.setText("No words available")
            if self.is_fullscreen:
                self.update_fullscreen_display()
    
    def update_progress(self):
        """Update progress bar and label."""
        if not self.metadata or not self.metadata.words:
            return
        
        total = len(self.metadata.words)
        current = self.current_index + 1
        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(self.current_index)
        self.progress_label.setText(f"{current} / {total} words ({percentage}%)")
    
    def load_last_file(self):
        """Load the last opened file if available."""
        last_file = self.file_history.get_last_file()
        if last_file and os.path.exists(last_file):
            # Ask user if they want to load the last file
            reply = QMessageBox.question(
                self,
                "Load Last File?",
                f"Would you like to load the last file you were reading?\n\n{os.path.basename(last_file)}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.parse_file(last_file)
    
    def update_recent_files(self):
        """Update the recent files dropdown."""
        self.recent_files_combo.blockSignals(True)
        self.recent_files_combo.clear()
        
        history = self.file_history.get_history()
        if history:
            for file_path in history:
                # Show just filename in dropdown
                filename = os.path.basename(file_path)
                # Set full path as data
                self.recent_files_combo.addItem(filename, file_path)
                # Set tooltip with full path
                index = self.recent_files_combo.count() - 1
                self.recent_files_combo.setItemData(index, file_path, Qt.ItemDataRole.ToolTipRole)
            
            self.recent_files_combo.setEnabled(True)
        else:
            self.recent_files_combo.setEnabled(False)
        
        self.recent_files_combo.blockSignals(False)
    
    def on_recent_file_selected(self, text: str):
        """Handle recent file selection from dropdown."""
        if not text:
            return
        
        # Get the full path from item data
        index = self.recent_files_combo.currentIndex()
        if index >= 0:
            file_path = self.recent_files_combo.itemData(index, Qt.ItemDataRole.ToolTipRole)
            if file_path and os.path.exists(file_path):
                self.parse_file(file_path)
    
    def closeEvent(self, event):
        """Clean up on window close."""
        # Save current position before closing
        if self.file_path and self.metadata:
            self.file_history.save_position(self.file_path, self.current_index)
        
        self.tts.cleanup()
        event.accept()

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
    QGroupBox, QProgressBar, QMessageBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
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
        self.wpm: int = 300  # Words per minute
        self.file_path: Optional[str] = None
        self.tts = TTSManager()
        self.file_history = FileHistory()
        
        self.init_ui()
        self.setup_timer()
        self.update_recent_files()  # Initialize recent files dropdown
        self.load_last_file()  # Ask to load last file
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Speed Reader")
        self.setGeometry(100, 100, 1100, 800)
        
        # Apply modern stylesheet
        self.setStyleSheet(get_stylesheet('dark'))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
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
        
        # Position info display (page, chapter, percentage)
        info_layout = QHBoxLayout()
        self.page_label = QLabel("Page: -")
        self.page_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        self.chapter_label = QLabel("Chapter: -")
        self.chapter_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        self.percentage_label = QLabel("Progress: 0%")
        self.percentage_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        
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
        self.context_preview.setMinimumHeight(180)
        self.context_preview.setMaximumHeight(220)
        self.context_preview.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                line-height: 1.6;
            }
        """)
        position_layout.addWidget(self.context_preview)
        
        position_group.setLayout(position_layout)
        
        # Word display area
        display_group = QGroupBox("Reading Display")
        display_layout = QVBoxLayout()
        
        self.word_label = QLabel("Load a file to begin reading")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("""
            QLabel {
                font-size: 56px;
                font-weight: 600;
                padding: 60px 40px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1e1e1e);
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 12px;
                letter-spacing: 2px;
            }
        """)
        display_layout.addWidget(self.word_label)
        display_group.setLayout(display_layout)
        
        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        
        # WPM and TTS controls
        top_controls = QHBoxLayout()
        
        wpm_layout = QHBoxLayout()
        wpm_layout.addWidget(QLabel("Words Per Minute (WPM):"))
        self.wpm_spinbox = QSpinBox()
        self.wpm_spinbox.setMinimum(50)
        self.wpm_spinbox.setMaximum(1000)
        self.wpm_spinbox.setValue(self.wpm)
        self.wpm_spinbox.valueChanged.connect(self.on_wpm_changed)
        wpm_layout.addWidget(self.wpm_spinbox)
        
        # TTS checkbox
        self.tts_checkbox = QCheckBox("Text-to-Speech")
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
        
        button_layout.addWidget(self.prev_word_btn)
        button_layout.addWidget(self.play_pause_btn)
        button_layout.addWidget(self.next_word_btn)
        button_layout.addWidget(self.reset_btn)
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
        layout.addWidget(display_group, stretch=1)
        layout.addWidget(controls_group)
        layout.addLayout(progress_layout)
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        QShortcut(QKeySequence("Space"), self, self.toggle_play_pause)
        QShortcut(QKeySequence("Left"), self, self.previous_word)
        QShortcut(QKeySequence("Right"), self, self.next_word)
        QShortcut(QKeySequence("R"), self, self.reset_position)
    
    def setup_timer(self):
        """Setup the timer for word display."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_next_word)
    
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
        self.tts.set_wpm(value)
        if self.is_playing:
            self.start_reading()
    
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
            return
        
        if 0 <= self.current_index < len(self.metadata.words):
            word = self.metadata.words[self.current_index]
            self.word_label.setText(word)
            
            # Speak the word if TTS is enabled
            if self.tts.enabled:
                self.tts.speak(word)
        else:
            self.word_label.setText("No words available")
    
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

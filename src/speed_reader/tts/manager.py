"""
Text-to-Speech manager for speed reader.
Handles speech synthesis with adjustable speed matching WPM.
Uses Windows SAPI directly for better control.
"""
import pyttsx3
import threading
import queue
from typing import Optional


class TTSManager:
    """Manages text-to-speech functionality."""
    
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None
        self.enabled: bool = False
        self.base_rate: int = 200  # Base words per minute for TTS
        self._current_rate: int = 200
        self._word_queue: queue.Queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_worker: threading.Event = threading.Event()
        
        try:
            self.engine = pyttsx3.init()
            # Set default properties
            self.engine.setProperty('rate', self.base_rate)
            self._current_rate = self.base_rate
        except Exception as e:
            print(f"Warning: Could not initialize TTS engine: {e}")
            self.engine = None
    
    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None
    
    def set_enabled(self, enabled: bool):
        """Enable or disable TTS."""
        was_enabled = self.enabled
        self.enabled = enabled and self.is_available()
        
        if self.enabled and not was_enabled:
            self._start_worker()
        elif not self.enabled:
            self._stop_worker.set()
            self._clear_queue()
    
    def _start_worker(self):
        """Start the worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._stop_worker.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def _worker_loop(self):
        """Worker thread that processes the queue."""
        # Create a separate engine for this thread
        try:
            worker_engine = pyttsx3.init()
        except Exception:
            return
        
        while not self._stop_worker.is_set():
            try:
                # Get word from queue with timeout
                try:
                    word = self._word_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                if word is None:
                    break
                
                # Clear queue if it's getting too full (keep only current word)
                while self._word_queue.qsize() > 1:
                    try:
                        self._word_queue.get_nowait()
                    except queue.Empty:
                        break
                
                # Set rate and speak
                try:
                    worker_engine.setProperty('rate', self._current_rate)
                    worker_engine.say(word)
                    worker_engine.runAndWait()
                except Exception as e:
                    print(f"TTS error: {e}")
                
                self._word_queue.task_done()
            except Exception:
                continue
    
    def set_wpm(self, wpm: int):
        """Set the speech rate based on WPM."""
        if not self.engine:
            return
        
        min_rate = 50
        max_rate = 300
        rate = max(min_rate, min(max_rate, int(wpm)))
        self._current_rate = rate
        
        try:
            self.engine.setProperty('rate', rate)
        except Exception:
            pass
    
    def speak(self, text: str):
        """Queue a word to be spoken."""
        if not self.enabled or not self.engine:
            return
        
        # Ensure worker is running
        if not self._worker_thread or not self._worker_thread.is_alive():
            self._start_worker()
        
        # Add to queue (will replace old words if queue is full)
        try:
            self._word_queue.put_nowait(text)
        except queue.Full:
            # Queue full, clear and add
            self._clear_queue()
            try:
                self._word_queue.put_nowait(text)
            except queue.Full:
                pass
    
    def _clear_queue(self):
        """Clear the queue."""
        while not self._word_queue.empty():
            try:
                self._word_queue.get_nowait()
            except queue.Empty:
                break
    
    def stop(self):
        """Stop current speech."""
        self._stop_worker.set()
        self._clear_queue()
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
    
    def cleanup(self):
        """Clean up TTS resources."""
        self.stop()

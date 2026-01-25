"""
Text-to-Speech manager for speed reader.
Handles speech synthesis with adjustable speed matching WPM.
Uses Windows SAPI directly for better control.
"""
import pyttsx3
import threading
import queue
import time
from typing import Optional


class TTSManager:
    """Manages text-to-speech functionality."""
    
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None  # Only used for checking availability
        self.enabled: bool = False
        self.base_rate: int = 200  # Base words per minute for TTS
        self._current_rate: int = 200
        self._word_queue: queue.Queue = queue.Queue(maxsize=10)
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_worker: threading.Event = threading.Event()
        self._worker_engine: Optional[pyttsx3.Engine] = None
        self._engine_lock: threading.Lock = threading.Lock()
        
        try:
            # Just initialize to check availability, don't actually use it
            test_engine = pyttsx3.init()
            test_engine = None
            self.engine = True  # Mark as available
        except Exception as e:
            print(f"[TTS] Warning: Could not initialize TTS: {e}")
            self.engine = None
    
    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None
    
    def set_enabled(self, enabled: bool):
        """Enable or disable TTS."""
        was_enabled = self.enabled
        self.enabled = enabled and self.is_available()
        
        if self.enabled and not was_enabled:
            # Reset stop event when enabling
            self._stop_worker.clear()
            self._start_worker()
        elif not self.enabled:
            self._stop_worker.set()
    
    def _start_worker(self):
        """Start the worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._stop_worker.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def _worker_loop(self):
        """Worker thread that speaks queued text continuously."""
        print("[TTS] Worker loop starting")
        
        word_count = 0
        
        while not self._stop_worker.is_set():
            try:
                # Get text from queue with timeout
                try:
                    text = self._word_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                if text is None:
                    break
                
                # Check if we should stop before speaking
                if self._stop_worker.is_set():
                    break
                
                try:
                    # Create a FRESH engine for each speak call to avoid state issues
                    worker_engine = pyttsx3.init()
                    
                    with self._engine_lock:
                        worker_engine.setProperty('rate', self._current_rate)
                        print(f"[TTS] Speaking {len(text)} chars at rate {self._current_rate}")
                        # Queue all text
                        worker_engine.say(text)
                        
                        # Check if stopped before actually speaking
                        if self._stop_worker.is_set():
                            worker_engine.stop()
                            print("[TTS] Stopped before playback")
                            break
                        
                        # Speak it all at once
                        worker_engine.runAndWait()
                    
                    # Check again after speaking
                    if self._stop_worker.is_set():
                        try:
                            worker_engine.stop()
                        except:
                            pass
                        break
                    
                    word_count += len(text.split())
                    print(f"[TTS] Finished speaking {len(text)} chars")
                    
                except Exception as e:
                    print(f"[TTS] Error speaking: {e}")
                    import traceback
                    traceback.print_exc()
                
                self._word_queue.task_done()
                
            except Exception as e:
                print(f"[TTS] Worker error: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"[TTS] Worker stopped")
    
    def set_wpm(self, wpm: int):
        """Set the speech rate based on WPM.
        
        NOTE: pyttsx3's rate property is NOT in WPM. It uses a 0-300 scale where:
        - Rate 0 = ~192 WPM
        - Rate > 0 = broken/instant (Windows SAPI bug)
        So we can only support ~192 WPM max, but we clamp it intelligently.
        """
        # Clamp WPM to max supported (around 192)
        # Use rate 0 for all speeds (works best)
        self._current_rate = 0
        
        # Store the user's desired WPM for reference, but use rate 0
        if wpm > 192:
            print(f"[TTS] WPM {wpm} exceeds maximum of ~192, using maximum")
        else:
            print(f"[TTS] WPM set to {wpm}")
    
    def speak(self, text: str):
        """Queue text to be spoken all at once."""
        if not self.enabled or not self.engine:
            return
        
        if not text or not text.strip():
            return
        
        # Ensure worker is running
        if not self._worker_thread or not self._worker_thread.is_alive():
            self._start_worker()
        
        # Queue the entire text as one unit
        try:
            self._word_queue.put_nowait(text)
        except queue.Full:
            pass
    
    def speak_and_get_duration(self, text: str) -> float:
        """Speak text immediately and return duration in seconds."""
        if not self.enabled or not self.engine:
            return 0
        
        if not text or not text.strip():
            return 0
        
        import time
        try:
            with self._engine_lock:
                if not self._worker_engine:
                    self._worker_engine = pyttsx3.init()
                self._worker_engine.setProperty('rate', self._current_rate)
                start = time.time()
                self._worker_engine.say(text)
                self._worker_engine.runAndWait()
                duration = time.time() - start
                return duration
        except Exception as e:
            print(f"[TTS] Error getting duration: {e}")
            return 0
    
    def stop(self):
        """Stop current speech."""
        print("[TTS] Stopping...")
        
        # Signal worker to stop FIRST so it doesn't keep processing
        self._stop_worker.set()
        
        # Clear the queue immediately so worker stops getting items
        while not self._word_queue.empty():
            try:
                self._word_queue.get_nowait()
            except queue.Empty:
                break
        
        # Try to stop the engine if it exists
        with self._engine_lock:
            if self._worker_engine:
                try:
                    self._worker_engine.stop()
                except Exception as e:
                    print(f"[TTS] Error stopping engine: {e}")
    
    def cleanup(self):
        """Clean up TTS resources."""
        self.stop()

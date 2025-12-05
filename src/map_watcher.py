from __future__ import annotations

from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

__all__ = ["MapWatcher"]


class _Handler(FileSystemEventHandler):
  def __init__(self, callback: Callable[[FileSystemEvent], None]):
    super().__init__()
    self._callback = callback

  def on_modified(self, event: FileSystemEvent):
    if not event.is_directory:
      self._callback(event)

  def on_created(self, event: FileSystemEvent):
    if not event.is_directory:
      self._callback(event)


class MapWatcher:
  def __init__(self, directory: str | Path, on_change: Callable[[Path], None]):
    self._directory = Path(directory).resolve()

    # Normalise callback to accept *Path* objects.
    self._on_change = lambda e: on_change(Path(e.src_path))

    handler = _Handler(self._on_change)
    self._observer = Observer()
    self._observer.schedule(handler, str(self._directory), recursive=False)
    self._observer.daemon = True
    self._observer.start()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb):
    self.stop()

  def stop(self):
    """Stops watching and waits for the background thread to exit."""
    self._observer.stop()
    try:
      self._observer.join(timeout=0.5)
    except RuntimeError:
      pass

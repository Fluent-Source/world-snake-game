"""Utility to watch a level directory for changes and invoke a callback.

Requires the `watchdog` package which provides efficient cross-platform
filesystem notifications.

Usage
-----
from src.map_watcher import MapWatcher

watcher = MapWatcher(path_to_watch, on_change)
...
watcher.stop()   # when finished
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

__all__ = ["MapWatcher"]


class _Handler(FileSystemEventHandler):
  """Internal event handler that forwards *file* changes and creations."""

  def __init__(self, callback: Callable[[FileSystemEvent], None]):
    super().__init__()
    self._callback = callback

  def on_modified(self, event: FileSystemEvent):  # noqa: N802 – watchdog naming
    if not event.is_directory:
      self._callback(event)

  def on_created(self, event: FileSystemEvent):  # noqa: N802 – watchdog naming
    if not event.is_directory:
      self._callback(event)


class MapWatcher:
  """Watches a directory and calls a callback as soon as a file changes.

  It runs a :class:`watchdog.observers.Observer` in its own background
  thread so that the main PyGame loop is never blocked.
  """

  def __init__(self, directory: str | Path, on_change: Callable[[Path], None]):
    self._directory = Path(directory).resolve()

    # Normalise callback to accept *Path* objects.
    self._on_change = lambda e: on_change(Path(e.src_path))

    handler = _Handler(self._on_change)
    self._observer = Observer()
    self._observer.schedule(handler, str(self._directory), recursive=False)
    # Use a daemon thread so the app shuts down even if user forgets stop().
    self._observer.daemon = True
    self._observer.start()

  # The MapWatcher itself can be used as a context-manager to ensure we stop
  # the observer in case of early exits or unhandled exceptions.
  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb):
    self.stop()

  def stop(self):
    """Stops watching and waits for the background thread to exit."""
    self._observer.stop()
    # Wait at most half a second so we don't block quitting forever.
    try:
      self._observer.join(timeout=0.5)
    except RuntimeError:
      # Already joined / never started – safe to ignore.
      pass

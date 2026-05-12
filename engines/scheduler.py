"""Subprocess file-based scheduler with status tracking and queue management."""
from __future__ import annotations

import json
import time
from enum import Enum
from pathlib import Path
from typing import Any


class SchedulerState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class Scheduler:
    """File-based IPC scheduler for background data extraction tasks."""

    def __init__(self, work_dir: str = "output/.scheduler") -> None:
        self._work_dir = Path(work_dir)
        self._work_dir.mkdir(parents=True, exist_ok=True)
        self._status_file = self._work_dir / "status.json"
        self._queue_file = self._work_dir / "queue.json"
        self._ensure_files()

    def _ensure_files(self) -> None:
        if not self._status_file.exists():
            self._write_status({"state": SchedulerState.IDLE, "last_run": None, "error": None})
        if not self._queue_file.exists():
            self._write_queue([])

    def _write_status(self, status: dict) -> None:
        with open(self._status_file, "w") as f:
            json.dump(status, f, indent=2, default=str)

    def _read_status(self) -> dict:
        if not self._status_file.exists():
            return {"state": SchedulerState.IDLE, "last_run": None, "error": None}
        with open(self._status_file) as f:
            return json.load(f)

    def _write_queue(self, queue: list) -> None:
        with open(self._queue_file, "w") as f:
            json.dump(queue, f, indent=2, default=str)

    def _read_queue(self) -> list:
        if not self._queue_file.exists():
            return []
        with open(self._queue_file) as f:
            return json.load(f)

    def get_status(self) -> dict:
        return self._read_status()

    def enqueue(self, task: dict) -> None:
        queue = self._read_queue()
        task["queued_at"] = time.time()
        task["status"] = "pending"
        queue.append(task)
        self._write_queue(queue)

    def start_next(self) -> dict | None:
        status = self._read_status()
        if status.get("state") == SchedulerState.RUNNING:
            return None
        queue = self._read_queue()
        pending = [t for t in queue if t.get("status") == "pending"]
        if not pending:
            return None
        task = pending[0]
        task["status"] = "running"
        task["started_at"] = time.time()
        self._write_queue(queue)
        self._write_status({"state": SchedulerState.RUNNING, "current_task": task, "last_run": time.time(), "error": None})
        return task

    def complete(self, success: bool = True, error: str | None = None) -> None:
        state = SchedulerState.DONE if success else SchedulerState.FAILED
        self._write_status({"state": state, "last_run": time.time(), "error": error})
        queue = self._read_queue()
        for t in queue:
            if t.get("status") == "running":
                t["status"] = "done" if success else "failed"
                t["completed_at"] = time.time()
        self._write_queue(queue)

    def reset(self) -> None:
        self._write_status({"state": SchedulerState.IDLE, "last_run": None, "error": None})
        self._write_queue([])

# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import threading
import time
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from weblate.utils.lock import (
    WeblateLock,
    WeblateLockNotLockedError,
    WeblateLockTimeoutError,
)
from weblate.utils.unittest import tempdir_setting


class WeblateLockTest(SimpleTestCase):
    """Test WeblateLock implementation."""

    @tempdir_setting("DATA_DIR")
    def test_basic_lock(self) -> None:
        """Test basic lock acquisition and release."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        lock = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="basic",
            slug="test-slug",
        )

        # Lock should not be locked initially
        self.assertFalse(lock.is_locked)

        # Acquire lock
        with lock:
            self.assertTrue(lock.is_locked)

        # Lock should be released
        self.assertFalse(lock.is_locked)

    @tempdir_setting("DATA_DIR")
    def test_reentrant_lock(self) -> None:
        """Test that locks are reentrant within the same thread."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        lock = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="reentrant",
            slug="test-slug",
        )

        # Nested lock acquisition
        with lock:
            self.assertTrue(lock.is_locked)
            with lock:
                self.assertTrue(lock.is_locked)
                with lock:
                    self.assertTrue(lock.is_locked)
                self.assertTrue(lock.is_locked)
            self.assertTrue(lock.is_locked)

        # Lock should be released after all contexts exit
        self.assertFalse(lock.is_locked)

    @tempdir_setting("DATA_DIR")
    def test_lock_timeout(self) -> None:
        """Test lock timeout when lock is held by another operation."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        lock1 = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="timeout",
            slug="test-slug",
            timeout=1,
        )

        lock2 = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="timeout",
            slug="test-slug",
            timeout=1,
        )

        # Acquire first lock
        with lock1:
            # Try to acquire second lock (should timeout)
            with self.assertRaises(WeblateLockTimeoutError):
                with lock2:
                    pass

    @tempdir_setting("DATA_DIR")
    def test_lock_release_error(self) -> None:
        """Test error when releasing a lock that was not held."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        lock = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="error",
            slug="test-slug",
        )

        # Manually call __exit__ without __enter__
        with self.assertRaises(WeblateLockNotLockedError):
            lock.__exit__(None, None, None)

    @tempdir_setting("DATA_DIR")
    def test_threading_separate_locks(self) -> None:
        """Test that different threads can use their own locks independently."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        results = {"thread1": False, "thread2": False}
        errors = []

        def thread1_func():
            try:
                lock = WeblateLock(
                    lock_path=str(lock_path),
                    scope="test",
                    key="thread1",
                    slug="test-slug",
                )
                with lock:
                    self.assertTrue(lock.is_locked)
                    time.sleep(0.1)
                    results["thread1"] = True
                self.assertFalse(lock.is_locked)
            except Exception as e:
                errors.append(("thread1", e))

        def thread2_func():
            try:
                lock = WeblateLock(
                    lock_path=str(lock_path),
                    scope="test",
                    key="thread2",
                    slug="test-slug",
                )
                with lock:
                    self.assertTrue(lock.is_locked)
                    time.sleep(0.1)
                    results["thread2"] = True
                self.assertFalse(lock.is_locked)
            except Exception as e:
                errors.append(("thread2", e))

        t1 = threading.Thread(target=thread1_func)
        t2 = threading.Thread(target=thread2_func)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Check no errors occurred
        if errors:
            self.fail(f"Errors in threads: {errors}")

        # Both threads should have completed successfully
        self.assertTrue(results["thread1"])
        self.assertTrue(results["thread2"])

    @tempdir_setting("DATA_DIR")
    def test_threading_shared_lock_instance(self) -> None:
        """Test that the same lock instance can be used from different threads."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        # Create a single lock instance to be shared across threads
        lock = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="shared",
            slug="test-slug",
        )

        results = {"thread1": False, "thread2": False}
        errors = []

        def thread1_func():
            try:
                # Each thread should be able to check if locked
                # Initially should not be locked in this thread
                self.assertFalse(lock.is_locked)
                with lock:
                    # Should be locked in this thread
                    self.assertTrue(lock.is_locked)
                    time.sleep(0.1)
                    results["thread1"] = True
                # Should not be locked after release in this thread
                self.assertFalse(lock.is_locked)
            except Exception as e:
                errors.append(("thread1", e))

        def thread2_func():
            try:
                # Wait a bit to let thread1 acquire the lock first
                time.sleep(0.05)
                # Each thread should be able to check if locked
                # This thread should see its own depth (0) - not locked from its perspective
                self.assertFalse(lock.is_locked)
                # Try to acquire - should succeed once thread1 releases
                with lock:
                    self.assertTrue(lock.is_locked)
                    results["thread2"] = True
                self.assertFalse(lock.is_locked)
            except Exception as e:
                errors.append(("thread2", e))

        t1 = threading.Thread(target=thread1_func)
        t2 = threading.Thread(target=thread2_func)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Check no errors occurred
        if errors:
            self.fail(f"Errors in threads: {errors}")

        # Both threads should have completed successfully
        self.assertTrue(results["thread1"])
        self.assertTrue(results["thread2"])

    @tempdir_setting("DATA_DIR")
    def test_threading_reentrant_per_thread(self) -> None:
        """Test that reentrancy works correctly per thread."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        lock = WeblateLock(
            lock_path=str(lock_path),
            scope="test",
            key="reentrant-thread",
            slug="test-slug",
        )

        errors = []
        results = {"nested_depth": 0}

        def thread_func():
            try:
                # Each thread should be able to acquire the lock multiple times
                with lock:
                    self.assertTrue(lock.is_locked)
                    with lock:
                        self.assertTrue(lock.is_locked)
                        with lock:
                            self.assertTrue(lock.is_locked)
                            results["nested_depth"] = 3
                        self.assertTrue(lock.is_locked)
                    self.assertTrue(lock.is_locked)
                self.assertFalse(lock.is_locked)
            except Exception as e:
                errors.append(e)

        t = threading.Thread(target=thread_func)
        t.start()
        t.join()

        if errors:
            self.fail(f"Errors in thread: {errors}")

        self.assertEqual(results["nested_depth"], 3)

    @tempdir_setting("DATA_DIR")
    def test_lock_attributes(self) -> None:
        """Test lock attributes and error messages."""
        lock_path = Path(self.settings.DATA_DIR) / "locks"
        lock_path.mkdir(exist_ok=True)

        lock = WeblateLock(
            lock_path=str(lock_path),
            scope="test-scope",
            key="test-key",
            slug="test-slug",
            origin="test-origin",
        )

        self.assertEqual(lock.scope, "test-scope")
        self.assertEqual(lock.origin, "test-origin")

        error_msg = lock.get_error_message()
        self.assertIn("test-origin", error_msg)
        self.assertIn("test-scope", error_msg)

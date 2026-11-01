"""
Security & Licensing Module - Local-First & Permanent Free Edition
No remote telemetry, no external subscription server, no network dependencies.
"""

import os
import hashlib
import getpass
import subprocess
import datetime
import time
import uuid

# Disabled remote server URL - local-first mode
LICENSE_SERVER_URL = "http://127.0.0.1:0"

def get_hwid() -> str:
    """Generate a consistent machine HWID locally."""
    try:
        user = getpass.getuser()
        node = str(uuid.getnode())
        raw = f"{user}-{node}-HikariDub-Permanent"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()
    except Exception:
        return "LOCAL-PERMANENT-HWID"

def check_license_online(hwid: str, app_version: str = "2.7"):
    """
    Local-first license check.
    Always returns 'premium' status with lifetime validity.
    Completely functional offline without internet connection.
    """
    return "premium", "Ứng dụng sẵn sàng"

def check_for_update(current_version_str: str):
    """
    Safe offline update check.
    Returns (has_update: bool, update_info: dict or None).
    """
    return False, None

def send_error_report(hwid: str, message: str, log_content: str = "", attach_file_path = None, pc_name: str = "Local PC"):
    """
    Safe local error logging instead of transmitting data to remote server.
    """
    try:
        log_dir = os.path.join(os.getcwd(), "Logs")
        os.makedirs(log_dir, exist_ok=True)
        report_file = os.path.join(log_dir, "local_error_reports.log")
        with open(report_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] HWID: {hwid} | PC: {pc_name}\n")
            f.write(f"Message: {message}\n")
            if log_content:
                f.write(f"Details: {log_content}\n")
            f.write("-" * 50 + "\n")
        return True, "Đã ghi nhận báo cáo vào nhật ký cục bộ (Logs/local_error_reports.log)"
    except Exception as e:
        return False, str(e)


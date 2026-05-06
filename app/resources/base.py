import logging
import os

from flask import g, has_request_context, request, session
from flask_login import current_user

import app.storage.db as db


class ResourceAuditMixin:
    """Shared audit logging for resource-layer calls."""

    def _log_resource_access(self, action: str, *, target_id=None, metadata=None) -> None:
        if not has_request_context():
            return
        if os.getenv("ENABLE_RESOURCE_AUDIT_LOGGING", "true").lower() not in {"1", "true", "yes", "on"}:
            return
        if getattr(g, "_resource_audit_logged", False) or getattr(g, "_resource_audit_logging_in_progress", False):
            return

        try:
            g._resource_audit_logging_in_progress = True

            user_id = session.get("_user_id")
            user_email = None
            # Avoid touching current_user here because that can invoke the
            # user_loader, which itself goes through audited resources.
            loaded_user = getattr(g, "_login_user", None)
            if loaded_user is not None:
                user_email = getattr(loaded_user, "email", None)
                if user_id is None:
                    user_id = getattr(loaded_user, "id", None)

            forwarded_for = request.headers.get("X-Forwarded-For", "")
            ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr

            db.insert_security_audit_log(
                {
                    "user_id": int(user_id) if user_id is not None else None,
                    "user_email": user_email,
                    "http_method": request.method,
                    "request_path": request.path,
                    "endpoint": request.endpoint,
                    "ip_address": ip_address,
                    "user_agent": request.user_agent.string if request.user_agent else None,
                    "resource_name": self.__class__.__name__,
                    "resource_action": action,
                    "target_id": target_id,
                    "request_metadata": metadata or {},
                }
            )
            g._resource_audit_logged = True
        except Exception:
            logging.getLogger(__name__).warning(
                "Failed to persist resource audit log for %s.%s",
                self.__class__.__name__,
                action,
                exc_info=True,
            )
        finally:
            g._resource_audit_logging_in_progress = False

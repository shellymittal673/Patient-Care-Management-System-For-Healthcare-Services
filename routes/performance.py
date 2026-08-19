from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required

from models.request_log import RequestLog
from routes.utils import roles_required

performance_bp = Blueprint("performance", __name__, url_prefix="/performance")


@performance_bp.route("/")
@login_required
@roles_required("admin")
def dashboard():
    from app import APP_START_TIME

    logs = RequestLog.query.order_by(RequestLog.created_at.desc()).limit(500).all()
    total = len(logs)

    if total:
        avg_response = round(sum(l.response_time_ms for l in logs) / total)
        error_count = sum(1 for l in logs if l.status_code >= 400)
        error_rate = round((error_count / total) * 100, 2)
    else:
        avg_response, error_rate = 0, 0.0

    uptime_seconds = (datetime.utcnow() - APP_START_TIME).total_seconds()
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))

    # Response time trend: most recent 30 requests, oldest first, for the chart
    trend = list(reversed(logs[:30]))
    trend_labels = [l.created_at.strftime("%H:%M:%S") for l in trend]
    trend_values = [l.response_time_ms for l in trend]

    # Performance by module (blueprint): average response time
    by_module = {}
    for l in logs:
        if not l.blueprint:
            continue
        by_module.setdefault(l.blueprint, []).append(l.response_time_ms)
    module_perf = [
        {"module": mod, "avg_ms": round(sum(times) / len(times)), "count": len(times)}
        for mod, times in sorted(by_module.items())
    ]

    return render_template(
        "performance_dashboard.html",
        total_requests=total, avg_response=avg_response, error_rate=error_rate,
        uptime_str=uptime_str, trend_labels=trend_labels, trend_values=trend_values,
        module_perf=module_perf,
    )

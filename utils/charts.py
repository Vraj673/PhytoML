"""
utils/charts.py
-----------------
Reusable data-aggregation helpers that turn raw `Prediction` rows into
small (labels, values) lists ready to hand to Chart.js on the frontend.
Shared by both the user dashboard (filtered to one user) and the admin
dashboard (unfiltered, across every user) — pass `user_id=None` for the
admin, site-wide view.
"""

from datetime import datetime, timedelta
from flask_babel import format_date
from sqlalchemy import func

from models import db, Prediction


def daily_prediction_counts(user_id=None, days=14):
    """
    Returns (labels, values) — number of predictions made on each of the
    last `days` days, zero-filled so the chart has no gaps.
    """
    since = datetime.utcnow() - timedelta(days=days - 1)

    query = db.session.query(
        func.date(Prediction.created_at).label("day"),
        func.count(Prediction.id).label("count"),
    ).filter(Prediction.created_at >= since)
    if user_id is not None:
        query = query.filter(Prediction.user_id == user_id)

    rows = query.group_by(func.date(Prediction.created_at)).all()
    counts_by_day = {str(r.day): r.count for r in rows}

    labels, values = [], []
    for i in range(days):
        day = (since + timedelta(days=i)).date()
        labels.append(format_date(day, "MMM d"))
        values.append(counts_by_day.get(str(day), 0))
    return labels, values


def disease_class_rows(user_id=None):
    """Returns [(class_label, count), ...] — most common first."""
    query = db.session.query(Prediction.predicted_class, func.count(Prediction.id))
    if user_id is not None:
        query = query.filter(Prediction.user_id == user_id)
    return (
        query.group_by(Prediction.predicted_class)
        .order_by(func.count(Prediction.id).desc())
        .all()
    )


def disease_class_counts(user_id=None):
    """Returns (labels, values) — how many predictions fell into each disease class."""
    rows = disease_class_rows(user_id)
    labels = [cls.replace("___", " - ").replace("_", " ") for cls, _count in rows]
    values = [count for _cls, count in rows]
    return labels, values


def healthy_vs_diseased_counts(user_id=None):
    """Returns (healthy_count, diseased_count) across all matching predictions."""
    query = Prediction.query
    if user_id is not None:
        query = query.filter(Prediction.user_id == user_id)
    total = query.count()
    healthy = query.filter(Prediction.predicted_class.contains("healthy")).count()
    return healthy, total - healthy

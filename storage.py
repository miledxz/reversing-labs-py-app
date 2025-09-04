from sqlalchemy.orm import Session
from models import RequestLog
from typing import Dict, Any, Optional
from datetime import datetime


def save_log(db: Session, headers: Dict[str, str], params: Dict[str, Any], data: Dict[str, Any]) -> RequestLog:
    log = RequestLog(user_agent=headers.get("user-agent", ""), host=headers.get("host", ""), params=params, data=data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def query_logs(db: Session, start: Optional[datetime], end: Optional[datetime]):
    q = db.query(RequestLog)
    if start:
        q = q.filter(RequestLog.created_at >= start)
    if end:
        q = q.filter(RequestLog.created_at <= end)
    q = q.order_by(RequestLog.created_at.desc())
    return q.all()
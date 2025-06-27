from ..utils.log import get_activity_log, ActivityLog
from fastapi import Depends
from typing import Annotated

ActivityLogger = Annotated[ActivityLog, Depends(get_activity_log)]

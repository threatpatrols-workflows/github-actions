#
# Copyright [2025] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from logging import getLogger

logger = getLogger(__name__)


class ThreatPatrolsBaseException(Exception):
    def __init__(self, *args, **kwargs):
        log_message = " ".join([str(x) for x in args]).strip()
        if log_message:
            logger.error(f"{log_message}")
        if "detail" in kwargs:
            logger.error(f"{kwargs['detail']}".strip())
        super().__init__(*args)


class ThreatPatrolsException(ThreatPatrolsBaseException):
    pass

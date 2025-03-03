import logging
from typing import Optional

import pydantic

from datahub.configuration.common import AllowDenyPattern
from datahub.ingestion.source.state.stateful_ingestion_base import (
    StatefulIngestionConfig,
    StatefulIngestionConfigBase,
)
from datahub.ingestion.source.usage.usage_common import BaseUsageConfig
from datahub.ingestion.source_config.sql.snowflake import BaseSnowflakeConfig

logger = logging.getLogger(__name__)


class SnowflakeStatefulIngestionConfig(StatefulIngestionConfig):
    """
    Specialization of basic StatefulIngestionConfig to adding custom config.
    This will be used to override the stateful_ingestion config param of StatefulIngestionConfigBase
    in the SnowflakeUsageConfig.
    """

    ignore_old_state = pydantic.Field(False, alias="force_rerun")


class SnowflakeUsageConfig(
    BaseSnowflakeConfig, BaseUsageConfig, StatefulIngestionConfigBase
):
    options: dict = {}
    database_pattern: AllowDenyPattern = AllowDenyPattern(
        deny=[r"^UTIL_DB$", r"^SNOWFLAKE$", r"^SNOWFLAKE_SAMPLE_DATA$"]
    )
    email_domain: Optional[str]
    schema_pattern: AllowDenyPattern = AllowDenyPattern.allow_all()
    table_pattern: AllowDenyPattern = AllowDenyPattern.allow_all()
    view_pattern: AllowDenyPattern = AllowDenyPattern.allow_all()
    apply_view_usage_to_tables: bool = False
    stateful_ingestion: Optional[SnowflakeStatefulIngestionConfig] = None

    @pydantic.validator("role", always=True)
    def role_accountadmin(cls, v):
        if not v or v.lower() != "accountadmin":
            # This isn't an error, since the privileges can be delegated to other
            # roles as well: https://docs.snowflake.com/en/sql-reference/account-usage.html#enabling-account-usage-for-other-roles
            logger.info(
                'snowflake usage tables are only accessible by role "accountadmin" by default; you set %s',
                v,
            )
        return v

    def get_sql_alchemy_url(self):
        return super().get_sql_alchemy_url(
            database="snowflake",
            username=self.username,
            password=self.password,
            role=self.role,
        )

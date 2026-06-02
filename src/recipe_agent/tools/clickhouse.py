from __future__ import annotations

from typing import Any

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import BaseTool


def build_tool(
    db_uri: str | None = None,
    model: Any | None = None,
    sample_rows_in_table_info: int = 3,
) -> list[BaseTool]:

    db = SQLDatabase.from_uri(
        db_uri,
        sample_rows_in_table_info=sample_rows_in_table_info,
    )
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    return toolkit.get_tools()

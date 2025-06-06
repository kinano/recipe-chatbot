import os

from datetime import datetime

from arize.exporter import ArizeExportClient
from arize.utils.types import Environments

client = ArizeExportClient()

print("#### Exporting your primary dataset into a dataframe.")

columns = [
    "context.span_id",
    "attributes.llm.output_messages",
    "attributes.llm.input_messages",
    "attributes.metadata",
    "annotation.notes",
    "annotation.acceptable.label",
]


traces_df = client.export_model_to_df(
    space_id="U3BhY2U6MjAwNTY6N04yWA==",
    model_id="recipe-chatbot",
    environment=Environments.TRACING,
    start_time=datetime.fromisoformat("2025-06-01T14:00:00.000+00:00"),
    end_time=datetime.fromisoformat("2025-06-06T14:01:01.284+00:00"),
    where=f"attributes.metadata.experiment = {os.environ.get('EXPERIMENT')}",  # and annotation.acceptable.label is not null and annotation.notes is not null"
    # Optionally specify columns to improve query performance
    columns=columns,
)
df_rows_length = traces_df.shape[0]

print(f"Number of rows: {df_rows_length}")

# print("\nFirst row of the dataframe:")
# print(traces_df.iloc[0].to_dict())
with open("/users/kinan/Desktop/traces_df.json", "w") as f:
    traces_df.to_json(f, orient="records", lines=True)

# TODOs:
# Failure patterns deduced by Claude from human notes only: https://claude.ai/share/e3ec1107-b96e-46f3-9be0-745e8af5e983
# Failure patterns deduced by Claude from LLM output with human notes: https://claude.ai/artifacts/a0eaa818-58d7-49d3-af6f-f9beeabae6f2
#

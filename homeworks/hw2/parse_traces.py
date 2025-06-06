import os

from datetime import datetime

from arize.exporter import ArizeExportClient
from arize.utils.types import Environments

client = ArizeExportClient()

print("#### Exporting your primary dataset into a dataframe.")


primary_df = client.export_model_to_df(
    space_id="U3BhY2U6MjAwNTY6N04yWA==",
    model_id="recipe-chatbot",
    environment=Environments.TRACING,
    start_time=datetime.fromisoformat("2025-06-01T14:00:00.000+00:00"),
    end_time=datetime.fromisoformat("2025-06-06T14:01:01.284+00:00"),
    where=f"attributes.metadata.experiment = {os.environ.get('EXPERIMENT')} and annotation.notes is  null",
    # Optionally specify columns to improve query performance
    columns=[
        "context.span_id",
        "attributes.output.value",
        "attributes.llm.output_messages",
        "attributes.metadata",
        "annotation.notes",
    ],
)
df_rows_length = primary_df.shape[0]

print(f"Number of rows: {df_rows_length}")

# print("\nFirst row of the dataframe:")
# print(primary_df.iloc[0].to_dict())

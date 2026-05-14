import pandas as pd
from pyarrow import flight

# --- Configuration ---
# Dremio Arrow Flight port is 32010 (as defined in your docker-compose)
FLIGHT_URL = "grpc://localhost:32010" 
USERNAME = "laimeng"      # Your Dremio user
PASSWORD = "password123"  # Your Dremio password
CATALOG = "Nessie_catalog"

# 1. Connect to the Dremio Flight Server
client = flight.FlightClient(FLIGHT_URL)

# 2. Authenticate
# Note: Flight uses Basic Auth under the hood
token = client.authenticate_basic_token(USERNAME, PASSWORD)
options = flight.FlightCallOptions(headers=[token])

# 3. Define the query
# Let's query one of the Iceberg tables you just created!
table_name = "balance_sheet_iceberg"
query = f'SELECT * FROM "{CATALOG}"."{table_name}" LIMIT 10'

print(f"Executing Query: {query}\n")

# 4. Execute the query and fetch the results
# get_flight_info tells the server to prepare the query execution
flight_info = client.get_flight_info(flight.FlightDescriptor.for_command(query), options)

# We grab the first (and usually only) endpoint to stream the data from
endpoint = flight_info.endpoints[0]
reader = client.do_get(endpoint.ticket, options)

# 5. Read the data directly into a PyArrow Table...
arrow_table = reader.read_all()

# 6. ...and convert it to a Pandas DataFrame for easy viewing/manipulation!
df = arrow_table.to_pandas()

# Display the results
print("Results:")
print(df)
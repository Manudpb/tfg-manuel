from google.cloud import bigquery

# TODO: Uncomment the line below to set the `project` variable.
# project = 'user-project-id'
#
# The `project` variable defines the project to be billed for query
# processing. The user must have the bigquery.jobs.create permission on
# this project to run a query. See:
# https://cloud.google.com/bigquery/docs/access-control#permissions

client = bigquery.Client.from_service_account_json("../testtfg-401316-89ed686b30cd.json")

query_string = """SELECT contracts.address, min(transactions.block_number), max(transactions.block_number),
COUNT(*) AS tx_count
FROM `bigquery-public-data.crypto_ethereum.contracts` AS contracts
JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions
ON (transactions.to_address = contracts.address)
WHERE transactions.block_number BETWEEN 11100000 AND 11199999
GROUP BY contracts.address
ORDER BY tx_count DESC
LIMIT 10

"""
query_job = client.query(query_string)  # API request
rows = query_job.result()  # Waits for query to finish
# Print the results.

print("address min max count")
rows.to_dataframe()
for row in rows:  # Wait for the job to complete.
    row
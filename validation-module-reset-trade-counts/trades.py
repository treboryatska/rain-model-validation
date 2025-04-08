import requests
import json
import pandas as pd
import time
import datetime

def execute_query(url, query, variables=None):
    """Sends the GraphQL query to the specified URL and returns the JSON response."""
    
    # Set the headers
    headers = {"Content-Type": "application/json"}
    # Prepare the payload
    json_payload = {"query": query}

    if variables:
        json_payload["variables"] = variables # Add variables dictionary to payload

    print(f"\nSending query to: {url} \nVariables: {variables}\n")
    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=json_payload, timeout=60)

        # Check for HTTP errors (like 4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON response
        result = response.json()
        return result

    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}") # Print response body on error
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response.")
        print(f"Response content: {response.text}")
        return None

def fetch_trades_for_order(subgraph_url, graphql_query, target_order_hash, start_date_str, end_date_str):
    """Fetches all trades for a specific order using pagination."""

    start_dt_utc = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    start_timestamp_inclusive = int(start_dt_utc.timestamp())
    end_dt_utc = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    end_timestamp_exclusive = int(end_dt_utc.timestamp())
    
    # define the page size
    page_size = 100

    # begin pagination loop
    all_trades_rows = []
    current_last_timestamp = end_timestamp_exclusive
    fetch_more = True

    print(f"\nFetching trades for order {target_order_hash} \nBetween dates: {start_date_str} (star timestamp: {start_timestamp_inclusive}) and {end_date_str} (end timestamp: {end_timestamp_exclusive}) exclusive\n")

    while fetch_more:
        print(f"Querying for trades before timestamp: {current_last_timestamp} \n")

        # Prepare variables for the current query page
        variables = {
            "orderHash": target_order_hash,
            "startTs": start_timestamp_inclusive,
            "endTs": end_timestamp_exclusive,
            "pageSize": page_size,
            "lastTs": current_last_timestamp # Use the timestamp from the last item of the previous batch
        }

        # Execute the query and print the results
        query_result = execute_query(subgraph_url, graphql_query, variables)

        # Handle failed query or errors
        if not query_result or "errors" in query_result or "data" not in query_result:
            print("Query failed, received errors, or no data found. Stopping.")
            if query_result and "errors" in query_result:
                print("GraphQL Errors:", json.dumps(query_result["errors"], indent=2))
            fetch_more = False
            break # Exit the loop on error or no data
        
        # Process successful query result
        orders_data = query_result["data"].get("orders", [])
        if not orders_data:
            print("No order found matching the hash (should not happen if hash is correct). Stopping.")
            fetch_more = False
            break
        
        # Assuming only one order matches the hash
        order_data = orders_data[0]
        order_hash = order_data.get("orderHash")
        trades_batch = order_data.get("trades", [])

        print(f"Received {len(trades_batch)} trades in this batch.")

        if not trades_batch:
            # No more trades match the criteria
            fetch_more = False
            print("No more trades match the criteria. Exiting loop.")
            break # Exit loop - all data fetched
        
        # Process this batch of trades and add to our list
        for trade in trades_batch:
            input_change = trade.get("inputVaultBalanceChange", {})
            input_token_info = input_change.get("vault", {}).get("token", {})
            output_change = trade.get("outputVaultBalanceChange", {})
            output_token_info = output_change.get("vault", {}).get("token", {})
            transaction_info = trade.get("tradeEvent", {}).get("transaction", {})

            row_data = {
                "order_hash": order_hash,
                "block_number": transaction_info.get("blockNumber"),
                "tx_hash": transaction_info.get("id"), # Tx Hash
                "trade_id": trade.get("id"), # Trade ID
                "trade_timestamp": trade.get("timestamp"), # Keep as string initially
                "input_token": input_token_info.get("symbol"),
                "input_decimals": input_token_info.get("decimals"), # Added decimals
                "input_amount": input_change.get("amount"),
                "input_old_vault_balance": input_change.get("oldVaultBalance"),
                "input_new_vault_balance": input_change.get("newVaultBalance"),
                "output_token": output_token_info.get("symbol"),
                "output_decimals": output_token_info.get("decimals"), # Added decimals
                "output_amount": output_change.get("amount"),
                "output_old_vault_balance": output_change.get("oldVaultBalance"),
                "output_new_vault_balance": output_change.get("newVaultBalance"),
            }
            all_trades_rows.append(row_data)

        # --- Prepare for next iteration ---
        # Update the last_timestamp to the timestamp of the *last* item in the current batch
        # Convert to int for the next query's 'where' clause
        current_last_timestamp = int(trades_batch[-1]['timestamp'])

        # Optimization: Check if we received fewer items than requested size
        if len(trades_batch) < page_size:
            print("Received fewer items than page size, assuming end of data.")
            fetch_more = False # Exit loop after processing this last batch
        else:
            print("Waiting briefly before next request...")
            time.sleep(0.5) # 500 milliseconds

    print(f"\nFinished fetching data. Total trades retrieved: {len(all_trades_rows)}")

    # Create and Display DataFrame
    if all_trades_rows:
        df = pd.DataFrame(all_trades_rows)

        desired_columns_order = [
            "order_hash", "block_number", "tx_hash", "trade_id", "trade_timestamp",
            "input_token", "input_decimals", "input_amount", "input_old_vault_balance", "input_new_vault_balance",
            "output_token", "output_decimals", "output_amount", "output_old_vault_balance", "output_new_vault_balance"
        ]
        df = df.reindex(columns=desired_columns_order)

        # print sample columns of the dataframe
        print("\nCreated DataFrame:")
        print(df[["order_hash", "block_number", "tx_hash", "input_token", "output_token"]].head(5).to_string())
        df.info()

        # Convert relevant columns to numeric types
        print("\nConverting numeric string columns...")
        numeric_cols = [
            'trade_timestamp', # Convert timestamp too
            'input_decimals', 'input_amount', 'input_old_vault_balance', 'input_new_vault_balance',
            'output_decimals', 'output_amount', 'output_old_vault_balance', 'output_new_vault_balance'
        ]
        # block_number can also be converted if needed
        # df['block_number'] = pd.to_numeric(df['block_number'], errors='coerce').astype('Int64') # Use nullable Int

        for col in numeric_cols:
            if col in df.columns:
                # Convert large numbers potentially needing float or object for very large ints
                df[col] = pd.to_numeric(df[col], errors='coerce')

        print("\nDataFrame Info after numeric conversion:")
        df.info()
        print("\nDataFrame Head after numeric conversion:")
        print(df.head(5))
        return df
    else:
        print("\nNo trades found or retrieved.")
        return None

# get the trade info
def get_trades(trade_hash, url, start_date_str, end_date_str):

    # define the GraphQL Query
    graphql_query = """
    query strategyTrades(
        $orderHash: ID!,
        $startTs: BigInt!,
        $endTs: BigInt!,
        $pageSize: Int!,
        $lastTs: BigInt  # Nullable: Timestamp of the last item from the previous page
    ) {
        orders(where: {orderHash: $orderHash}) {
        orderHash
        trades(
            first: $pageSize,
            orderBy: timestamp,
            orderDirection: desc,
            where: { timestamp_gte: $startTs, timestamp_lt: $lastTs }
            ) {
            id
            timestamp
            inputVaultBalanceChange {
            vault { token { symbol decimals } }
            amount
            oldVaultBalance
            newVaultBalance
            }
            outputVaultBalanceChange {
            vault { token { symbol decimals } }
            amount
            oldVaultBalance
            newVaultBalance
            }
            tradeEvent {
            transaction { id blockNumber }
            }
        }
        }
    }
    """

    # get the trades dataframe
    try:
        
        df_trades = fetch_trades_for_order(
            url, 
            graphql_query, 
            trade_hash, 
            start_date_str,
            end_date_str
        )
        
        return df_trades
    except Exception as e:
        print(f"Error: {e}")
        return None
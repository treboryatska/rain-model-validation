# get the trade data from the order
import requests

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
        response = requests.post(url, headers=headers, json=json_payload, timeout=30)

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
    
# return information about the order
def get_order_info(order_hash, url):
    query = """
        query order($orderHash: ID!) {
            orders(where: {orderHash: $orderHash}) {
                id
                orderHash
                active
                timestampAdded
                trades(orderBy: timestamp, orderDirection: desc, first: 1) {
                    inputVaultBalanceChange {
                        vault { token { symbol } }
                    }
                    outputVaultBalanceChange {
                        vault { token { symbol } }
                    }
                }
            }
        }
    """

    order_response = execute_query(url, query, {"orderHash": order_hash})
    order_data = order_response["data"]["orders"][0]

    return order_data
from datetime import datetime

# define the raindex graphql api

# create a dictionary of subgraph endpoints - one for each chain
subgraph_urls = {
		"flare": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-flare/2024-12-13-9dc7/gn",
		"base": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-base/2024-12-13-9c39/gn",
		"polygon": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-matic/2024-12-13-d2b4/gn",
		"arbitrum": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-arbitrum-one/2024-12-13-7435/gn",
		"bsc": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-bsc/2024-12-13-2244/gn",
		"linea": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-linea/2024-12-13-09c7/gn",
		"ethereum": "https://api.goldsky.com/api/public/project_clv14x04y9kzi01saerx7bxpg/subgraphs/ob4-mainnet/2024-12-13-7f22/gn"
	}

def parse_flexible_date(date_string, output_format="%Y-%m-%d"):
    """Tries parsing a date string with multiple formats."""
    possible_formats = [
        "%m/%d/%Y",  # MM/DD/YYYY
        "%Y-%m-%d",  # YYYY-MM-DD
        "%m/%d/%y",  # MM/DD/YY
        "%d-%b-%Y",  # DD-Mon-YYYY (e.g., 01-Oct-2024)
        # Add more formats as needed
    ]
    
    for fmt in possible_formats:
        try:
            # Try parsing with the current format
            date_obj = datetime.strptime(date_string, fmt)
            # If successful, format to the desired output format and return
            return date_obj.strftime(output_format)
        except ValueError:
            # If this format failed, continue to the next one
            continue
            
    # If none of the formats worked, raise an error or return None/default
    print(f"Error: Could not parse date '{date_string}' with any known format.")
    return None 
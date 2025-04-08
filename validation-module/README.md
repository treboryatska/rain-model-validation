## Raindex strategies - model validation

This module runs a statistical comparison between actual DSF strategy results and outputs from a modeled DSF strategy using real market data as inputs.

Use main.py as the entrypoint. The required parameters are network, target_order_hash, start_date_str, and end_date_str.

Ensure the actual market data inputs to the model have the same date range as parameters start_date_str and end_date_str from main.py.

### to do
- identify sample of order hashes for analysis
   - needs to be large enough to give us assurance in results
- need testing scripts for basic outliers in this module
- ingestion for modeled outputs (all order hashes in sample)
   - ask Sid of he can help here
- run statistical comparison of trade count between resets actuals to modeled outputs
- explain methodology and results

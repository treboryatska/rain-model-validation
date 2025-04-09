## Raindex strategies - model validation

This module runs a statistical comparison between actual DSF strategy results and outputs from a modeled DSF strategy using real market data as inputs.

Use main.py as the entrypoint. The required parameters are network, target_order_hash, start_date_str, and end_date_str.

Ensure the actual market data inputs to the model have the same date range as parameters start_date_str and end_date_str from main.py.

### Validation steps

- Get the order hash of the implemented strategy (e.g., 0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712)
- Choose a date range for the validation. The start date of the selected date range cannot be before the strategy implementation date
- Using the chosen date range retrieve market data for the strategy token pair (i.e., WFLR/cysFLR pool on Sparkdex; pool contract address: 0x6C58ac774f31aBe010437681C5365fD8d6a43adc)
- Use the market data as inputs to the model, https://docs.google.com/spreadsheets/d/1PCpkmEqENY3cXLrLDO7fVH5YQ5MyRMv7H8ErVcqDnkY/edit?gid=634861611#gid=634861611
  - The market data is input on the "Data" tab.
  - The required columns are block_number, dex_pool_address, tx_hash, token_amount_a, token_amount_b, timestamp
  - The first step should be to clear out any existing data in these columns
  - Note several things: (1) the Data tab is indifferent to which token is labeled as token_a or token_b, (2) the remaining columns cell reference the input data--these fields should not be modified or overwritten; and (3) the 'ABS USD' cell has a #REF error--ignore for now
- 

### to do
- identify sample of order hashes for analysis
   - needs to be large enough to give us assurance in results
- need testing scripts for basic outliers in this module
- ingestion for modeled outputs (all order hashes in sample)
   - ask Sid of he can help here
- run statistical comparison of trade count between resets actuals to modeled outputs
- explain methodology and results

## Raindex strategies - model validation

This module runs a statistical comparison between actual DSF strategy results and outputs from a modeled DSF strategy using real market data as inputs.

Use main.py as the entrypoint. The required parameters for main.py are model_file_path, network, target_order_hash, start_date_str, and end_date_str.

### Data input dates
We define three distinct datetime stamps: (1) strategy deployment, (2) strategy funding, and (3) strategy trading initiated. 

For modeling purposes, strategy trading state is tracked from the datetime stamp of the first strategy trade.

### Validation steps
Follow the below steps to validate modeled trade count between resets for a particular strategy order hash. 

Environment setup:
- clone the repo
- install python, along with pyenv
- in the local path where the repo was cloned, initiate pyenv with python version 3.13.0
- in the local path where the repo was cloned, create a python virtual environment (venv)
- activate the virtual environment, and install the requirements by running: pip install -r requirements.txt

Data inputs:
- Get the order hash of the implemented strategy (e.g., 0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712)
- Choose a date range for the validation.
  - Define start_date_str as item (3) in the "Data input dates" section above. You can find this date from the subgraph, or from https://v2.raindex.finance/. Note, raindex.finance automatically reports the timestamp of the trade in the browser's local timezone. You must convert the time to UTC. 
    - Note: the validation script will provide reasonable outputs so long as the start date used for the validation script matches the start date of market data used as inputs to the model
  - Choose an appropriate end_date_str. The validation script filters the modeled outputs to match the earlier of end_date_str or the timestamp of the last strategy trade retrieved from the subgraph. This means, if you choose an end_date_str beyond the last strategy trade date the analysis will filter the model outputs using the last strategy trade date. 
- Using the chosen date range retrieve market data for the strategy token pair
- Use the market data as inputs to the model, https://docs.google.com/spreadsheets/d/1PCpkmEqENY3cXLrLDO7fVH5YQ5MyRMv7H8ErVcqDnkY/edit?gid=634861611#gid=634861611
  - The market data is input on the "Data" tab.
  - Required columns: block_number, dex_pool_address, tx_hash, token_amount_a, token_amount_b, timestamp
  - The first step should be to clear out any existing data in the required columns
  - Note several things: (1) the Data tab is indifferent to which token is labeled as token_a or token_b, (2) all non-required columns cell reference the input data--these fields should not be modified or overwritten; and (3) the 'ABS USD' cell has a #REF error--ignore for now
- Rename the Google sheet to the standard format, {model_name}_{order_hash} e.g. model_1_0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712
- Reconfirm the start date in the selected range is the datetime stamp of the first trade in the strategy. You shouldn't have any market data before this date, and the date should be set for the variable start_date_str in main.py
- Navigate to the 'Data' tab in the model
- Download the Google sheet tab to your local computer as a *csv* file
- Navigate to the appropriate model tab e.g. 15M, 30M, etc. 
- Download the Google sheet tab to your local computer as a *csv* file
- Set the main.py input fields {model_input_file_path} and {model_output_file_path} to the respective local file paths
   - e.g. {Users/shared/downloads/model_1_0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712  - Test-15M.csv}
   - e.g. {/esers/shared/downloads/model_1_0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712  - Data.csv}
   - Note the file name on your local machine. csv file downloads are tab specific. The tab name is appended to the file name.

Run validation script:
- activate the virtual environment
- run main.py
- inspect the logs

Validation script execution path:
- user-defined validation parameters
- get order info and trades from subgraph
- get model input data from user-downloaded local csv
- get model output data from user-downloaded local csv
- concatenate model input data (market data) with strategy trades (actual resets) to get actual trade count between resets of the strategy
- run tests on modeled trade count between resets and actual trade count between resets

### Automated data input tests
- Validation will exit if the model file path is incorrect
- Validation will exit if it cannot find the columns "tx_hash" and "timestamp" in the model inputs csv
- Validation will exit if it cannot find the columns "Date/time" and "trade_count_in_reset" in the model outputs csv
- Validation will exit if the model outputs do not start at row 23 in the csv
- Check actual market data input date range. Warn the user when:
  -  Market data start date is > start_date_str from main.py
  -  Market data end date is < end_date_str from main.py

### to do
- testing scripts for basic outliers in this module
- run statistical comparison of trade count between resets actuals to modeled outputs
- explain methodology and results

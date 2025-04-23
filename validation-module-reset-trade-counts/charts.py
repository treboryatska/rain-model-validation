# create basic scatter plot charts for sample results

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import numpy as np
import scipy.stats as stats

# scatter plot function
def create_scatter_plot(df, x_column, y_column, category_column, ax=None):
    """
    Creates a scatter plot using Seaborn, colored by a categorical column.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        x_column (str): The name of the column for the x-axis.
        y_column (str): The name of the column for the y-axis.
        category_column (str): The name of the categorical column for coloring points (hue).
        ax (plt.Axes, optional): The Matplotlib Axes object to plot on.
                                 If None, Seaborn creates a plot on the current figure or a new one.
                                 Defaults to None.

    Returns:
        plt.Axes: The Axes object containing the plot.

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If any of the specified columns do not exist in the DataFrame.
        ValueError: If DataFrame is empty or if no valid data remains after
                    handling NaNs for the specified columns.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame 'df' is empty.")

    required_columns = [x_column, y_column, category_column]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {', '.join(missing_cols)}")

    # --- Data Preparation (Handle NaNs in plot-relevant columns) ---
    plot_data = df[required_columns].dropna()

    if plot_data.empty:
        raise ValueError(f"No valid, non-NaN data found for columns: {required_columns}")

    # --- Plotting using Seaborn ---
    # Seaborn handles figure/axes creation if ax is None
    # We might set figsize *before* if ax is None and we want control
    if ax is None:
        plt.figure(figsize=(12, 8)) # Example: Adjust size, legend needs space

    # Use hue for categorical coloring. Seaborn creates the legend automatically.
    ax = sns.scatterplot(data=plot_data, x=x_column, y=y_column, hue=category_column, ax=ax)

    # Set title (Seaborn might set labels, but we can override)
    ax.set_title(f"{x_column} vs {y_column} (colored by {category_column})")
    ax.set_xlabel(x_column) # Ensure labels are set if needed
    ax.set_ylabel(y_column)

    # Optional: Adjust legend position if it overlaps data
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title=category_column)

    return ax # Return the axes object

def create_faceted_histogram(df, value_column, category_column,
                             col_wrap=3, height=4, aspect=1.2,
                             kde=False, bins='auto', stat='count',
                             x_formatter='comma_formatter',
                             **hist_kwargs):
    """
    Creates a faceted histogram using Seaborn's displot, showing the distribution
    of a value separated by category, with each category in its own subplot.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        value_column (str): The name of the numeric column to plot the distribution of.
        category_column (str): The name of the categorical column to facet by (create subplots for).
        col_wrap (int, optional): Number of subplot columns before wrapping to the next row.
                                  Defaults to 3.
        height (float, optional): Height (in inches) of each facet. Defaults to 4.
        aspect (float, optional): Aspect ratio of each facet, so width = aspect * height.
                                  Defaults to 1.2.
        kde (bool, optional): If True, compute a kernel density estimate for each histogram.
                              Defaults to False.
        bins (str, int, sequence, optional): Specification of histogram bins.
                                             Passed to numpy.histogram_bin_edges.
                                             Defaults to 'auto'.
        stat (str, optional): Aggregate statistic to compute in each bin ('count',
                              'frequency', 'probability', 'density'). Defaults to 'count'.
        x_formatter (str, optional): The formatter to use for the x-axis. Defaults to 'comma_formatter'. Options are 'comma_formatter' or 'percent_formatter'.
        **hist_kwargs: Additional keyword arguments passed directly to the underlying
                       seaborn.histplot call within displot (e.g., element='step').

    Returns:
        seaborn.FacetGrid: The FacetGrid object managing the figure and axes.

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If value_column or category_column do not exist in the DataFrame.
        ValueError: If DataFrame is empty, if value_column is not numeric after cleaning,
                    or if no valid data remains after handling NaNs.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame 'df' is empty.")

    required_columns = [value_column, category_column]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {', '.join(missing_cols)}")

    # --- Data Preparation (Handle NaNs & ensure numeric value column) ---
    plot_data = df[required_columns].copy() # Use .copy() to avoid SettingWithCopyWarning

    # Ensure value column is numeric first before dropna, coerce errors
    try:
        numeric_col = pd.to_numeric(plot_data[value_column], errors='coerce')
        # Check if ALL values became NaN after coercion (meaning no numbers at all)
        if numeric_col.isna().all() and not df[value_column].isna().all():
             raise ValueError(f"Column '{value_column}' contains no numeric data after coercion.")
        plot_data[value_column] = numeric_col
    except Exception as e:
         raise TypeError(f"Could not convert column '{value_column}' to numeric: {e}")

    # Drop rows where EITHER the (now numeric) value or the category is missing
    plot_data = plot_data.dropna()

    if plot_data.empty:
        raise ValueError(f"No valid data remains for columns {required_columns} after handling NaNs.")

    # --- Plotting using Seaborn displot for faceting ---
    # This function creates the Figure and the grid of Axes (FacetGrid)
    # 1. Create the FacetGrid object, explicitly setting sharex=False
    g = sns.FacetGrid(
        data=plot_data,
        col=category_column,
        col_wrap=col_wrap,
        height=height,
        aspect=aspect,
        sharex=False,  # <<< Explicitly set independent X axes here
        sharey=False   # Keep independent Y axes too
    )

    # 2. Map the histogram plotting function onto the grid
    # Pass histogram-specific arguments here (bins, kde, stat, etc.)
    # Also pass **hist_kwargs (like edgecolor)
    if 'edgecolor' not in hist_kwargs: hist_kwargs['edgecolor'] = 'black' # Default edgecolor
    g.map(sns.histplot, value_column, bins=bins, kde=kde, stat=stat, **hist_kwargs)

    # --- Customize Titles and Labels (using FacetGrid methods) ---
    y_label = stat.capitalize() if stat != 'probability' else 'Proportion'
    if stat == 'count': y_label = 'Frequency (Count)'
    value_axis_label = value_column.replace('_', ' ').title()
    # Use g.set_axis_labels AFTER mapping the plot
    g.set_axis_labels(value_axis_label, y_label)
    g.set_titles("{col_name}")
    g.fig.suptitle(f'Distribution of {value_axis_label} by {category_column.replace("_"," ").title()}', y=1.03)


    # --- Format x-axis ticks with commas and rotate labels ---
    comma_formatter = FuncFormatter(lambda x, p: f"{int(x):,}")
    # --- Format x-axis ticks as percentages and rotate labels ---
    percent_formatter = FuncFormatter(lambda x, p: f"{x:.2%}")
    for ax in g.axes.flat:
        # Check if axes have data plotted (important for FacetGrid)
        if len(ax.patches) > 0 or len(ax.lines) > 0: # Check for bars or KDE lines
            if x_formatter == 'comma_formatter':
                ax.xaxis.set_major_formatter(comma_formatter)
            elif x_formatter == 'percent_formatter':
                ax.xaxis.set_major_formatter(percent_formatter)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Adjust layout at the very end
    # Use g.fig.tight_layout() when working with FacetGrid
    g.fig.tight_layout(rect=[0, 0, 1, 0.97])

    return g

# create a Q-Q plot
def create_qq_plot(df, value_column):
    """
    Creates a Q-Q plot using Seaborn, showing the distribution of a value
    separated by category, with each category in its own subplot.
    """

    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame 'df' is empty.")

    required_columns = [value_column]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {', '.join(missing_cols)}")

    # --- Data Preparation (Handle NaNs & ensure numeric value column) ---
    data_series = df[value_column]

    # Ensure value column is numeric first before dropna, coerce errors
    try:
        numeric_series = pd.to_numeric(data_series, errors='coerce')
        # Check if ALL values became NaN after coercion (meaning no numbers at all)
        # Check original series' nulls too, in case it was already all null
        if numeric_series.isna().all() and not data_series.isna().all():
             print(f"Warning: Column '{value_column}' contains no numeric data after coercion. Skipping plot.")
             raise ValueError(f"Column '{value_column}' contains no numeric data after coercion.")
    except Exception as e:
         raise TypeError(f"Could not convert column '{value_column}' to numeric: {e}")

    # Drop rows where (now numeric) value column is missing
    plot_data_cleaned = numeric_series.dropna()

    # --- Check if data remains after cleaning ---
    if plot_data_cleaned.empty:
        print(f"No valid, non-missing data found in column '{value_column}' to plot.")
        return

    # --- Create Q-Q plot using the cleaned data from the specific column ---
    fig = plt.figure(figsize=(12, 8)) # Create and capture the figure

    # Pass the cleaned 1D Series (plot_data_cleaned) to probplot, not the whole df
    stats.probplot(plot_data_cleaned, dist="norm", plot=plt)

    # Customize the plot titles and labels
    plt.title(f"Q-Q Plot for '{value_column}'")
    plt.xlabel("Theoretical Quantiles (Normal Distribution)")
    plt.ylabel("Sample Quantiles")
    plt.grid(True)

    return fig


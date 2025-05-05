# create basic scatter plot charts for sample results

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import numpy as np
import scipy.stats as stats
import matplotlib.dates as mdates

# line chart function
def create_line_chart(df, x_column, y_column, category_column=None, title=None, xlabel=None, ylabel=None, ax=None, figsize=(10, 6)):
    """
    Creates a line chart using Seaborn, optionally colored by a categorical column.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        x_column (str): The name of the column to use for the x-axis.
        y_column (str): The name of the column to use for the y-axis.
        category_column (str, optional): The name of the column to use for coloring
                                         different lines (hue). Defaults to None.
        title (str, optional): The title for the chart. Defaults to None.
        xlabel (str, optional): The label for the x-axis. Defaults to x_column name.
        ylabel (str, optional): The label for the y-axis. Defaults to y_column name.
        ax (matplotlib.axes.Axes, optional): An existing Axes object to plot on.
                                             If None, a new figure and axes are created.
                                             Defaults to None.
        figsize (tuple, optional): The size of the figure to create if ax is None.
                                   Defaults to (10, 6).

    Returns:
        tuple: A tuple containing:
            - fig (matplotlib.figure.Figure): The Figure object for the plot.
            - ax (matplotlib.axes.Axes): The Axes object containing the plot.

    Raises:
        ValueError: If specified columns are not found in the DataFrame.
        TypeError: If the input df is not a pandas DataFrame.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    required_columns = [x_column, y_column]
    if category_column:
        required_columns.append(category_column)

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # --- Plotting ---
    # Determine figure and axes
    if ax is None:
        # Create new figure and axes if none are provided
        fig, ax = plt.subplots(figsize=figsize)
    else:
        # If axes are provided, get the figure they belong to
        fig = ax.figure

    # Create the line plot using seaborn
    sns.lineplot(
        data=df,
        x=x_column,
        y=y_column,
        hue=category_column, # Use category_column for hue if provided
        ax=ax,
        marker='o', # Optional: add markers to points
        legend='auto' # Show legend if hue is used
    )

    # --- Styling ---
    # Set title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        # Generate a default title if none provided
        default_title = f"{y_column} over {x_column}"
        if category_column:
            default_title += f" by {category_column}"
        ax.set_title(default_title, fontsize=14, fontweight='bold')

    # Set labels
    ax.set_xlabel(xlabel if xlabel else x_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(ylabel if ylabel else y_column.replace('_', ' ').title(), fontsize=12)

    # Improve readability
    ax.tick_params(axis='x', rotation=45) # Rotate x-axis labels if needed
    ax.grid(axis='y', linestyle='--', alpha=0.7) # Add light grid lines

    # Adjust legend position if it exists
    legend_bbox_adjust = [0, 0, 1, 1] # Default rect for tight_layout if no legend outside
    if category_column and ax.get_legend() is not None:
        # Place legend outside the plot area to avoid overlap
        ax.legend(title=category_column.replace('_', ' ').title(), bbox_to_anchor=(1.05, 1), loc='upper left')
        # Adjust layout to make room for the legend
        legend_bbox_adjust = [0, 0, 0.80, 1] # Make right boundary smaller

    # Apply tight_layout to the figure
    # Use rect parameter to potentially leave space for legend if it's outside
    fig.tight_layout(rect=legend_bbox_adjust)

    # --- Return Figure and Axes ---
    return fig, ax # Always return both figure and axes


# Grouped vertical bar chart function
def create_grouped_bar_chart(
    df,
    category_column, # x-axis
    value_column,    # y-axis
    group_column,    # hue (groups within each category)
    title=None,
    xlabel=None,
    ylabel=None,
    ax=None,
    figsize=(12, 7), # Adjusted default size
    palette="viridis",
    add_bar_labels=True,
    label_format='{:,.0f}',
    xtick_rotation=45, # Default rotation for x-axis labels
    legend_loc='upper right' # New parameter for legend location
    ):
    """
    Creates a grouped vertical bar chart using Seaborn.

    Args:
        df (pd.DataFrame): The DataFrame containing the data in a "long" format.
                           (e.g., columns for category, value, and group type).
        category_column (str): The name of the column for the x-axis (categories).
        value_column (str): The name of the column for the y-axis (bar heights/values).
        group_column (str): The name of the column to group by (creates different colored bars
                            within each category).
        title (str, optional): The title for the chart. Defaults to None.
        xlabel (str, optional): The label for the x-axis. Defaults to category_column name.
        ylabel (str, optional): The label for the y-axis. Defaults to value_column name.
        ax (matplotlib.axes.Axes, optional): An existing Axes object to plot on.
                                             If None, a new figure and axes are created.
                                             Defaults to None.
        figsize (tuple, optional): The size of the figure to create if ax is None.
                                   Defaults to (12, 7).
        palette (str or list, optional): Seaborn color palette for the bars.
                                         Defaults to "viridis".
        add_bar_labels (bool, optional): If True, add data labels on top of the bars.
                                         Defaults to True.
        label_format (str, optional): Python format string for the bar labels.
                                      Defaults to '{:,.0f}' (comma-separated integer).
        xtick_rotation (int, optional): Rotation angle for x-axis tick labels.
                                        Defaults to 45. Set to 0 for no rotation.
        legend_loc (str, optional): Location for the legend (e.g., 'best', 'upper right').
                                    Defaults to 'upper right'. Set to None to hide legend.

    Returns:
        tuple: A tuple containing:
            - fig (matplotlib.figure.Figure): The Figure object for the plot.
            - ax (matplotlib.axes.Axes): The Axes object containing the plot.

    Raises:
        ValueError: If specified columns are not found in the DataFrame or if data is unsuitable.
        TypeError: If the input df is not a pandas DataFrame.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    required_columns = [category_column, value_column, group_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # Check if value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value_column]):
         # try to coerce the value column to a numeric type
         try:
             df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
         except Exception as e:
             raise ValueError(f"Value column '{value_column}' must be numeric. Error: {e}")

    # Check if data exists
    if df.empty:
        raise ValueError("Input DataFrame 'df' is empty.")

    # --- Data Preparation ---
    # Create a copy to avoid modifying the original DataFrame
    plot_df = df.copy()

    # --- Plotting ---
    # Determine figure and axes
    if ax is None:
        # Create new figure and axes if none are provided
        fig, ax = plt.subplots(figsize=figsize)
    else:
        # If axes are provided, get the figure they belong to
        fig = ax.figure

    # Create the grouped vertical bar plot using seaborn
    barplot = sns.barplot( # Assign the barplot to a variable
        data=plot_df,
        x=category_column, # Categories on x-axis
        y=value_column,    # Values on y-axis
        hue=group_column,  # Grouping variable
        palette=palette,   # Apply color palette
        ax=ax,
        errorbar=None      # *** Turn off confidence interval lines/error bars ***
    )

    # --- Styling ---
    # Set title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        # Generate a default title if none provided
        default_title = f"{value_column} by {category_column}, Grouped by {group_column}"
        ax.set_title(default_title, fontsize=14, fontweight='bold')

    # Set labels
    ax.set_xlabel(xlabel if xlabel else category_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(ylabel if ylabel else value_column.replace('_', ' ').title(), fontsize=12)

    # Improve readability
    ax.grid(axis='y', linestyle='--', alpha=0.7) # Add horizontal grid lines
    sns.despine(ax=ax) # Remove top and right spines

    # Rotate x-axis labels
    if xtick_rotation is not None and xtick_rotation != 0:
        ax.tick_params(axis='x', rotation=xtick_rotation)

    # Adjust legend position
    if legend_loc and ax.get_legend() is not None:
        # Place legend inside using specified location
        ax.legend(title=group_column.replace('_', ' ').title(), loc=legend_loc)
    elif ax.get_legend() is not None:
         # Remove legend if legend_loc is None or False
         ax.get_legend().remove()


    # --- Add Bar Labels ---
    if add_bar_labels:
        # Iterate through the containers (groups of bars) in the Axes object
        for container in ax.containers:
            ax.bar_label(
                container,
                fmt=label_format, # Apply user-defined format
                padding=3,        # Add some padding between bar and label
                fontsize=8        # Adjust font size (often needs to be smaller for grouped)
                # rotation=90    # Optional: rotate labels if they overlap
            )
        # Optional: Adjust y-axis limits slightly to make room for labels on tallest bars
        current_ylim = ax.get_ylim()
        # Ensure bottom limit is not negative if data is non-negative
        bottom_lim = 0 if current_ylim[0] >= 0 and plot_df[value_column].min() >= 0 else current_ylim[0]
        new_ylim_upper = current_ylim[1] * 1.08 # Increase upper limit by 8%
        ax.set_ylim(bottom=bottom_lim, top=new_ylim_upper)


    # Apply tight_layout AFTER potentially adjusting legend and limits
    fig.tight_layout()

    # --- Return Figure and Axes ---
    return fig, ax # Always return both figure and axes

# Faceted grouped vertical bar chart function
def create_faceted_grouped_bar_chart(
    df,
    category_column, # x-axis within each facet
    value_column,    # y-axis within each facet
    group_column,    # hue (groups within each category)
    facet_column,    # Column to create facets (subplots) by
    facet_wrap=None, # Number of columns for facet grid wrapping
    sharex=False,    # Share x-axis (categories)? Often False if categories differ per facet
    sharey=True,     # Share y-axis (values)? Often True if values are comparable
    title=None,
    palette=None,
    height=4,        # Height (in inches) of each facet
    aspect=1.2,      # Aspect ratio of each facet (width = height * aspect, adjusted default)
    add_bar_labels=True,
    label_format='{:,.0f}',
    xtick_rotation=45, # Default rotation for x-axis labels
    sort_categories=False, # Sorting categories less common for vertical grouped bars
    hspace=0.4,        # Controls height space between facet rows
    legend_loc='best'  # Default location if moved inside
    ):
    """
    Creates a faceted grid of vertical grouped bar charts using Seaborn's catplot.

    Args:
        df (pd.DataFrame): The DataFrame containing the data in a "long" format.
        category_column (str): The name of the column for the x-axis (categories).
        value_column (str): The name of the column for the y-axis (bar heights/values).
        group_column (str): The name of the column to group by (hue).
        facet_column (str): The name of the column to create facets by (using 'col').
        facet_wrap (int, optional): Number of columns to wrap facets into. Defaults to None (all facets in one row).
        sharex (bool, optional): Whether facets should share the x-axis (categories). Defaults to False.
        sharey (bool, optional): Whether facets should share the y-axis (values). Defaults to True.
        title (str, optional): The overall title for the FacetGrid figure. Defaults to None.
        palette (str or list, optional): Seaborn color palette for the bars. Defaults to "viridis".
        height (float, optional): Height (in inches) of each facet. Defaults to 4.
        aspect (float, optional): Aspect ratio of each facet, so width = height * aspect. Defaults to 1.2.
        add_bar_labels (bool, optional): If True, add data labels on top of the bars. Defaults to True.
        label_format (str, optional): Python format string for the bar labels. Defaults to '{:,.0f}'.
        xtick_rotation (int, optional): Rotation angle for x-axis tick labels. Defaults to 45.
        sort_categories (bool, optional): If True, attempts to sort categories (x-axis). Defaults to False.
        hspace (float, optional): Height space between subplot rows. Defaults to 0.4.
        legend_loc (str, optional): Location for the legend (e.g., 'best', 'upper right'). Defaults to 'best'.

    Returns:
        seaborn.FacetGrid: The FacetGrid object containing the plot grid.

    Raises:
        ValueError: If specified columns are not found in the DataFrame or if data is unsuitable.
        TypeError: If the input df is not a pandas DataFrame.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    required_columns = [category_column, value_column, group_column, facet_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # Check if value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value_column]):
         # try to coerce the value column to a numeric type
         try:
             df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
             # Check for NaNs after coercion, which indicates failed conversion for some rows
             if df[value_column].isnull().any():
                 print(f"Warning: Some values in '{value_column}' could not be converted to numeric and became NaN.")
         except Exception as e:
             raise ValueError(f"Value column '{value_column}' must be numeric. Coercion failed. Error: {e}")

    # Check if data exists
    if df.empty:
        raise ValueError("Input DataFrame 'df' is empty.")
    # Drop rows where the numeric value column ended up being NaN after coercion attempt
    plot_df = df.dropna(subset=[value_column]).copy()
    if plot_df.empty:
         raise ValueError(f"DataFrame is empty after removing rows with non-numeric values in '{value_column}'.")


    # --- Sorting (Optional) ---
    # Sort category order if requested
    category_order = None
    if sort_categories:
        # Example: Sort categories based on the mean value across all groups/facets
        # This is just one way, might need adjustment based on desired logic
        mean_vals = plot_df.groupby(category_column)[value_column].mean().sort_values(ascending=False)
        category_order = mean_vals.index.tolist()
        print(f"Sorting categories (x-axis) by mean value: {category_order}")


    # --- Plotting ---
    # Create the faceted plot using catplot
    g = sns.catplot(
        data=plot_df,
        x=category_column, # Category on x-axis for vertical bars
        y=value_column,    # Value on y-axis
        hue=group_column,  # Grouping variable
        col=facet_column,  # Faceting variable
        kind="bar",        # Specify bar chart type
        errorbar=None,     # Turn off error bars
        palette=palette,
        height=height,     # Height of each facet
        aspect=aspect,     # Aspect ratio of each facet
        col_wrap=facet_wrap, # Wrap facets into columns
        sharex=sharex,     # Control x-axis sharing
        sharey=sharey,     # Control y-axis sharing
        legend=True,       # *** Let catplot create the legend initially ***
        # legend_out=False, # Keep legend inside plot area initially (default)
        order=category_order # Apply category sorting if defined
    )

    # --- Styling and Labels ---
    # Add overall title
    if title:
        # Adjust y position slightly more if hspace is large or title is long
        title_y_pos = 1.02 + (hspace * 0.05) if facet_wrap and facet_wrap < len(plot_df[facet_column].unique()) else 1.02
        g.fig.suptitle(title, y=title_y_pos, fontsize=14, fontweight='bold')

    # Add bar labels if requested
    if add_bar_labels:
        for ax in g.axes.flat: # Iterate through all axes in the grid
             # Check if axes has any containers (bars) before trying to label
             if ax.containers:
                 for container in ax.containers:
                     try:
                         ax.bar_label(
                             container,
                             fmt=label_format,
                             padding=3,
                             fontsize=8, # Adjust font size for facets
                             rotation=0 # Usually no rotation needed for vertical
                         )
                     except Exception as e:
                          print(f"Warning: Could not add bar labels to an axis. Error: {e}")
                 # Adjust y-axis limits for labels if needed
                 try:
                     current_ylim = ax.get_ylim()
                     # Ensure bottom limit is not negative if data is non-negative
                     bottom_lim = 0 if current_ylim[0] >= 0 and plot_df[value_column].min() >= 0 else current_ylim[0]
                     new_ylim_upper = current_ylim[1] * 1.1 # Increase upper limit slightly more
                     ax.set_ylim(bottom=bottom_lim, top=new_ylim_upper)
                 except Exception as e:
                     print(f"Warning: Could not adjust ylim for an axis. Error: {e}")


    # Improve axis labels and grid (applied to each facet)
    g.set_axis_labels(
        x_var=category_column.replace('_', ' ').title(), # Now x is category
        y_var=value_column.replace('_', ' ').title()     # Now y is value
    )
    g.set_titles("{col_name}") # Set facet titles based on the facet_column values

    # Rotate x-axis tick labels (categories)
    g.set_xticklabels(rotation=xtick_rotation, ha='right', fontsize=9) # Adjust ha (horizontal alignment)
    g.tick_params(axis='y', labelsize=9)


    # Add grid lines to each facet
    for ax in g.axes.flat:
        ax.grid(axis='y', linestyle='--', alpha=0.7) # Horizontal grid lines

    # --- Move Legend ---
    # Access the legend created by catplot and move it if it exists
    if g.legend is not None:
        # Set the title for the existing legend
        g.legend.set_title(group_column.replace('_', ' ').title())
        # Move the legend using matplotlib's standard legend placement
        # sns.move_legend(g, loc=legend_loc) # Use seaborn's helper function
        # Or manually adjust bbox_to_anchor if needed:
        sns.move_legend(g, loc='upper right', bbox_to_anchor=(1, 1)) # Example: Top right corner of figure


    # Adjust layout AFTER potentially moving legend
    # Use subplots_adjust for potentially finer control than tight_layout with facets/legends
    # Adjust 'right' to make space for the legend if needed
    g.fig.subplots_adjust(top=0.92, right=0.88, hspace=hspace) # Adjust top for title, right for legend


    # --- Return FacetGrid Object ---
    return g

# Horizontal bar chart function
def create_horizontal_bar_chart(
    df,
    category_column,
    value_column,
    title=None,
    xlabel=None,
    ylabel=None,
    ax=None,
    figsize=(10, 8),
    top_n=None,
    palette="viridis",
    add_bar_labels=True, # New parameter to control bar labels
    label_format='{:,.0f}' # New parameter for label formatting (default: integer with comma)
    ):
    """
    Creates a horizontal bar chart using Seaborn, sorted by value.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        category_column (str): The name of the column for the y-axis (categories).
        value_column (str): The name of the column for the x-axis (bar lengths/values).
        title (str, optional): The title for the chart. Defaults to None.
        xlabel (str, optional): The label for the x-axis. Defaults to value_column name.
        ylabel (str, optional): The label for the y-axis. Defaults to category_column name.
        ax (matplotlib.axes.Axes, optional): An existing Axes object to plot on.
                                             If None, a new figure and axes are created.
                                             Defaults to None.
        figsize (tuple, optional): The size of the figure to create if ax is None.
                                   Defaults to (10, 8). Adjust height based on categories.
        top_n (int, optional): If specified, only plot the top N categories based on value.
                               Defaults to None (plot all).
        palette (str or list, optional): Seaborn color palette for the bars.
                                         Defaults to "viridis".
        add_bar_labels (bool, optional): If True, add data labels to the end of the bars.
                                         Defaults to True.
        label_format (str, optional): Python format string for the bar labels.
                                      Defaults to '{:,.0f}' (comma-separated integer).
                                      Use '{:,.2f}' for 2 decimal places, etc.

    Returns:
        tuple: A tuple containing:
            - fig (matplotlib.figure.Figure): The Figure object for the plot.
            - ax (matplotlib.axes.Axes): The Axes object containing the plot.

    Raises:
        ValueError: If specified columns are not found in the DataFrame or if data is unsuitable.
        TypeError: If the input df is not a pandas DataFrame.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    required_columns = [category_column, value_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # Check if value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value_column]):
         # try to coerce the value column to a numeric type
         try:
             df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
         except Exception as e:
             raise ValueError(f"Value column '{value_column}' must be numeric. Error: {e}")

    # --- Data Preparation ---
    # Create a copy to avoid modifying the original DataFrame
    plot_df = df.copy()

    # Sort by the value column in descending order
    plot_df = plot_df.sort_values(by=value_column, ascending=False)

    # Optionally select top N categories
    if top_n is not None and isinstance(top_n, int) and top_n > 0:
        plot_df = plot_df.head(top_n)
    elif top_n is not None:
        print("Warning: 'top_n' must be a positive integer. Plotting all categories.")

    # Check if data remains after filtering/sorting
    if plot_df.empty:
        raise ValueError("No data available to plot after sorting/filtering.")


    # --- Plotting ---
    # Determine figure and axes
    if ax is None:
        # Adjust default figsize height based on number of categories
        num_categories = plot_df[category_column].nunique()
        dynamic_height = max(6, num_categories * 0.4) # Adjust multiplier as needed
        figsize = (figsize[0], dynamic_height)
        # Create new figure and axes if none are provided
        fig, ax = plt.subplots(figsize=figsize)
    else:
        # If axes are provided, get the figure they belong to
        fig = ax.figure

    # Create the horizontal bar plot using seaborn
    barplot = sns.barplot( # Assign the barplot to a variable
        data=plot_df,
        x=value_column,
        y=category_column,
        palette=palette, # Apply color palette
        ax=ax,
    )

    # --- Styling ---
    # Set title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        # Generate a default title if none provided
        default_title = f"{value_column} by {category_column}"
        if top_n:
            default_title = f"Top {top_n} {default_title}"
        ax.set_title(default_title, fontsize=14, fontweight='bold')

    # Set labels
    ax.set_xlabel(xlabel if xlabel else value_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(ylabel if ylabel else category_column.replace('_', ' ').title(), fontsize=12)

    # Improve readability
    ax.grid(axis='x', linestyle='--', alpha=0.7) # Add vertical grid lines
    sns.despine(ax=ax) # Remove top and right spines

    # --- Add Bar Labels (New Section) ---
    if add_bar_labels:
        # Iterate through the containers (bars) in the Axes object
        for container in ax.containers:
            ax.bar_label(
                container,
                fmt=label_format, # Apply user-defined format
                padding=3,        # Add some padding between bar and label
                fontsize=9       # Adjust font size as needed
                )
        # Optional: Adjust x-axis limits slightly to make room for labels on longest bars
        # This prevents labels from being cut off if they extend beyond the default plot area.
        # You might need to adjust the multiplier (e.g., 1.05 or 1.1) based on label length/font size.
        current_xlim = ax.get_xlim()
        new_xlim_upper = current_xlim[1] * 1.08 # Increase upper limit by 8%
        ax.set_xlim(right=new_xlim_upper)


    # --- Return Figure and Axes ---
    return fig, ax # Always return both figure and axes

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


# cumulative sum bar chart
def plot_cumulative_trade_minutes_bar(
    df: pd.DataFrame,
    time_column: str,
    minutes_column: str,
    title: str = "Cumulative Minutes Between Trades Over Time",
    xlabel: str = "Trade Execution Time",
    ylabel: str = "Cumulative Minutes Between Trades",
    figsize: tuple = (12, 6),
    date_format: str = "%Y-%m-%d %H:%M", # Format for x-axis ticks
    color: str = 'skyblue', # Color for the bars
    # Bar width can be tricky with time series, often best left to default or calculated
    # bar_width: float | None = None
) -> plt.Axes:
    """
    Generates a cumulative bar chart showing the sum of minutes between trades
    against the trade execution time. Each bar represents a trade time.

    Args:
        df (pd.DataFrame): DataFrame containing the trade data.
        time_column (str): The name of the column containing trade execution timestamps
                           (should be datetime or convertible to datetime).
        minutes_column (str): The name of the column containing the minutes elapsed
                              since the *previous* trade. The first value might be NaN or 0.
        title (str, optional): The title for the plot.
                               Defaults to "Cumulative Minutes Between Trades Over Time".
        xlabel (str, optional): Label for the x-axis. Defaults to "Trade Execution Time".
        ylabel (str, optional): Label for the y-axis.
                               Defaults to "Cumulative Minutes Between Trades".
        figsize (tuple, optional): Figure size (width, height) in inches.
                                   Defaults to (12, 6).
        date_format (str, optional): The format string for displaying dates on the x-axis.
                                     Defaults to "%Y-%m-%d %H:%M".
        color (str, optional): The color for the bars. Defaults to 'skyblue'.
        # bar_width (float, optional): Width of the bars. If None, matplotlib attempts
        #                              to determine a reasonable width. Defaults to None.


    Returns:
        matplotlib.axes._axes.Axes: The Axes object containing the plot.

    Raises:
        ValueError: If specified columns are not found or have incorrect types.
        TypeError: If df is not a pandas DataFrame.
    """
    # --- Input Validation ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")

    required_columns = [time_column, minutes_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # --- Data Preparation ---
    plot_df = df.copy() # Work on a copy

    # Convert time column to datetime if it's not already
    try:
        if not pd.api.types.is_datetime64_any_dtype(plot_df[time_column]):
            plot_df[time_column] = pd.to_datetime(plot_df[time_column])
    except Exception as e:
        raise ValueError(f"Could not convert '{time_column}' to datetime: {e}")

    # Convert minutes column to numeric, coercing errors
    try:
        plot_df[minutes_column] = pd.to_numeric(plot_df[minutes_column], errors='coerce')
    except Exception as e:
        raise ValueError(f"Could not convert '{minutes_column}' to numeric: {e}")

    # Handle potential NaNs introduced by coercion or already present
    # Fill NaN with 0, assuming the first trade has 0 minutes before it,
    # or if there were conversion issues. You might adjust this logic.
    plot_df[minutes_column] = plot_df[minutes_column].fillna(0)

    # Sort by time - crucial for cumulative sum
    plot_df = plot_df.sort_values(by=time_column)

    # Calculate cumulative sum
    cumulative_col_name = f"cumulative_{minutes_column}"
    plot_df[cumulative_col_name] = plot_df[minutes_column].cumsum()

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=figsize) # Create figure and axes explicitly

    # Plot the bars
    # Note: Bar width with datetime axes can sometimes be tricky.
    # Matplotlib usually does a decent job by default.
    # You might need to calculate width based on time differences if default isn't good.
    ax.bar(
        plot_df[time_column],
        plot_df[cumulative_col_name],
        color=color,
        # width=bar_width # Uncomment and set if you need specific width control
        align='center' # Align bars on the center of the timestamp
    )

    # --- Styling and Labels ---
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    # Format x-axis for dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
    plt.xticks(rotation=45, ha='right') # Rotate labels for better readability

    # Add grid lines (optional for bar charts, can make them busy)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7) # Grid lines only on y-axis

    # Set y-axis limit to start from 0
    ax.set_ylim(bottom=0)

    # Improve layout
    plt.tight_layout()

    return ax # Return the Axes object
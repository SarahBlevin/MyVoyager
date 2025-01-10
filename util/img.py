import os
import matplotlib.pyplot as plt

def create_bar_chart(
    x_data,
    y_data,
    title,
    xlabel,
    ylabel,
    output_directory,
    output_dataset_name,
    output_filename,
    figsize,
    rotation=90
):
    """
    Creates a bar chart and saves it as an image.

    Parameters:
        x_data (list): Labels for the x-axis (e.g., module names).
        y_data (list): Values corresponding to x_data (e.g., usage counts).
        title (str): Title of the chart.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        output_directory (str): Directory where the image will be saved.
        output_filename (str): Name of the output image file (e.g., 'chart.png').
        figsize (tuple): Figure size (default: (12, 8)).
        rotation (int): Rotation angle for x-axis labels (default: 90).

    Returns:
        str: Full path to the saved image file.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Plot the bar chart
    plt.figure(figsize=figsize)
    plt.bar(x_data, y_data)
    plt.xticks(rotation=rotation)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    # Save the chart as an image
    output_path = os.path.join(output_directory,output_dataset_name, output_filename)
    plt.savefig(output_path)
    plt.close()  # Close the figure to avoid memory issues

    print(f"Chart saved to {output_path}")
    return output_path
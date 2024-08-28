# coding: utf-8
# @author: kaimin
# @time: 2024-05-14 17:09

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap


def visualize(path: str, dataset_length: str, p_model_name: str, ):
    """
    :param path:
    :param dataset_length:
    :param p_model_name:
    :return:
    """
    df = pd.read_csv(path)
    df['Context Length'] = df['dataset'].apply(lambda x: int(x.split('Length')[1].split('Depth')[0]))
    df['Document Depth'] = df['dataset'].apply(lambda x: x.split('Depth')[1].split('_')[0])

    # Exclude 'Context Length' and 'Document Depth' columns
    model_columns = [
        col for col in df.columns
        if col not in ['Context Length', 'Document Depth']
    ]

    for model_name in model_columns[1:]:
        model_df = df[['Document Depth', 'Context Length', model_name]].copy()
        model_df.rename(columns={model_name: 'Score'}, inplace=True)
        model_name = p_model_name

        # Create pivot table
        pivot_table = pd.pivot_table(model_df, values='Score', index=['Document Depth'], columns=['Context Length'], aggfunc='mean')

        # Calculate mean scores
        mean_scores = pivot_table.mean().values

        # Calculate overall score
        overall_score = mean_scores.mean()

        # Create heatmap and line plot
        plt.figure(figsize=(15.5, 8))
        ax = plt.gca()
        cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#F0496E', '#EBB839', '#0CD79F'])

        # Draw heatmap
        sns.heatmap(pivot_table, cmap=cmap, ax=ax, cbar_kws={'label': 'Score'}, vmin=0, vmax=100)

        # Set line plot data
        x_data = [i + 0.5 for i in range(len(mean_scores))]
        y_data = mean_scores

        # Create twin axis for line plot
        ax2 = ax.twinx()
        # Draw line plot
        ax2.plot(x_data, y_data, color='white', marker='o', linestyle='-', linewidth=2, markersize=8, label='Average Depth Score')
        # Set y-axis range
        ax2.set_ylim(0, 100)

        # Hide original y-axis ticks and labels
        ax2.set_yticklabels([])
        ax2.set_yticks([])

        # Add legend
        ax2.legend(loc='upper left')

        # Set chart title and labels
        ax.set_title(f'{model_name} {dataset_length} Context '
                     'Performance\nFact Retrieval Across '
                     'Context Lengths ("Needle In A Haystack")')

        ax.set_xlabel('Token Limit')
        ax.set_ylabel('Depth Percent')

        ax.set_xticklabels(pivot_table.columns.values, rotation=45)
        ax.set_yticklabels(pivot_table.index.values, rotation=0)

        # Add overall score as a subtitle
        plt.text(0.5, -0.13,
                 f'Overall Score for {model_name}: '
                 f'{overall_score:.2f}',
                 ha='center',
                 va='center',
                 transform=ax.transAxes,
                 fontsize=13)

        # Save heatmap as PNG
        png_file_path = path.replace('.csv', f'.png')
        plt.tight_layout()
        plt.subplots_adjust(right=1)
        plt.draw()
        plt.savefig(png_file_path)
        # plt.show()

        plt.close()  # Close figure to prevent memory leaks

        # Print saved PNG file path
        print(f'Heatmap for {model_name} saved as: {png_file_path}')

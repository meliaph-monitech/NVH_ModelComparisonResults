import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Function to load the summary table
def load_summary_data(file):
    return pd.read_csv(file)

# Function to load and plot CSV data with highlights based on predictions
def load_and_plot_csv_with_highlights(file_name, summary_df, selected_model):
    # Load the selected file
    if not os.path.exists(file_name):
        st.error(f"File '{file_name}' not found.")
        return

    raw_data = pd.read_csv(file_name)

    # Color mapping for predictions
    class_color_map = {
        0.0: "blue",
        1.0: "red",
        2.0: "green",
        3.0: "purple",
        4.0: "orange"
    }

    # Prepare the figure for Plotly
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)

    # Plot all data for the first column (in gray)
    fig.add_trace(
        go.Scatter(x=raw_data.index, y=raw_data.iloc[:, 0], mode='lines', line=dict(color='gray'), name='All Data (First Column)'),
        row=1, col=1
    )

    # Plot all data for the second column (in gray)
    fig.add_trace(
        go.Scatter(x=raw_data.index, y=raw_data.iloc[:, 1], mode='lines', line=dict(color='gray'), name='All Data (Second Column)'),
        row=2, col=1
    )

    # Highlight bead data based on the selected model's predictions
    file_info = summary_df[summary_df["file"] == os.path.basename(file_name)]
    
    added_classes = set()
    
    for idx, row in file_info.iterrows():
        start_idx = int(row["start_index"])
        end_idx = int(row["end_index"])
        prediction = row[selected_model]  # Use predictions for coloring
        
        if pd.isna(prediction):
            continue

        color = class_color_map.get(prediction, "black")  # Default to black if class not found
        linestyle = 'dash' if row["is_test"] else 'solid'

        # Add the highlighted data trace for the first column
        fig.add_trace(
            go.Scatter(
                x=raw_data.index[start_idx:end_idx+1],
                y=raw_data.iloc[start_idx:end_idx+1, 0],
                mode='lines',
                line=dict(color=color, dash=linestyle),
                name=f"Class {prediction}" if prediction not in added_classes else None
            ),
            row=1, col=1
        )

        # Add the highlighted data trace for the second column
        fig.add_trace(
            go.Scatter(
                x=raw_data.index[start_idx:end_idx+1],
                y=raw_data.iloc[start_idx:end_idx+1, 1],
                mode='lines',
                line=dict(color=color, dash=linestyle),
                name=f"Class {prediction}" if prediction not in added_classes else None
            ),
            row=2, col=1
        )
        
        added_classes.add(prediction)

    # Update layout and add axis labels
    fig.update_layout(
        title="Data Visualization with Predictions",
        xaxis_title="Index",
        yaxis_title="First Column Values",
        xaxis2_title="Index",
        yaxis2_title="Second Column Values",
        height=700,
        showlegend=True
    )

    # Show the plot in Streamlit
    st.plotly_chart(fig)

# Streamlit file uploader for summary CSV
st.title("CSV File Visualizer")

# Let user specify the folder path on their local system
folder_path = st.text_input("Enter Folder Path to CSV Files", "")

if folder_path:
    # Get the list of CSV files from the specified folder
    def get_csv_files_from_directory(directory):
        csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
        return csv_files

    # Get CSV files in the directory
    if os.path.exists(folder_path):
        csv_files = get_csv_files_from_directory(folder_path)
        
        if csv_files:
            # Create a dropdown for selecting the file
            selected_file = st.selectbox("Select CSV File to Plot", csv_files)

            # After selecting the CSV, the summary CSV file is uploaded
            uploaded_summary_file = st.file_uploader("Upload Summary CSV File", type=["csv"])

            if uploaded_summary_file:
                summary_df = load_summary_data(uploaded_summary_file)

                # Let user select model columns that end with "_Prediction"
                model_columns = [col for col in summary_df.columns if "_Prediction" in col]
                selected_model = st.selectbox("Select Model for Coloring", model_columns)

                # Show button for plotting data
                if st.button("Plot Data"):
                    file_path = os.path.join(folder_path, selected_file)
                    load_and_plot_csv_with_highlights(file_path, summary_df, selected_model)
        else:
            st.warning("No CSV files found in the specified directory.")
    else:
        st.error("The folder path does not exist.")

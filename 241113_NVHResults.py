import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Function to load the summary table
@st.cache_data
def load_summary_data(file_path):
    return pd.read_csv(file_path)

# Function to load and plot CSV data with highlights based on predictions
def load_and_plot_csv_with_highlights(file_name, summary_df, data_dir):
    # Load the selected file
    file_path = os.path.join(data_dir, file_name)
    if not os.path.exists(file_path):
        st.error(f"File '{file_name}' not found in {data_dir}")
        return

    raw_data = pd.read_csv(file_path)

    # Let the user select which model's predictions to use
    model_columns = [col for col in summary_df.columns if "_Prediction" in col]
    selected_model = st.selectbox("Select a model for predictions", model_columns)

    # Automatically find the corresponding "_Correct" column
    correct_column = selected_model.replace("_Prediction", "_Correct")

    # Plot data
    fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Plot all data for the first column
    axs[0].plot(raw_data.index, raw_data.iloc[:, 0], color="gray", label="All Data")
    axs[0].set_title(f"First Column Data (All Indices)")
    axs[0].set_ylabel("First Column Values")
    axs[0].grid()

    # Plot all data for the second column
    axs[1].plot(raw_data.index, raw_data.iloc[:, 1], color="gray", label="All Data")
    axs[1].set_title(f"Second Column Data (All Indices)")
    axs[1].set_xlabel("Index")
    axs[1].set_ylabel("Second Column Values")
    axs[1].grid()

    # Highlight bead data based on the selected model's predictions
    file_info = summary_df[summary_df["file"] == file_name]
    for idx, row in file_info.iterrows():
        start_idx = row["start_index"]
        end_idx = row["end_index"]
        bead_number = row["bead_number"]
        is_test = row["is_test"]
        prediction = row[selected_model]  # Use predictions for coloring
        correct = row[correct_column]     # Use correctness for labels

        # Skip highlighting for training data (NaN predictions)
        if pd.isna(prediction):
            continue

        # Highlight the range
        bead_data_indices = range(start_idx, end_idx + 1)
        class_color_map = {
            0.0: "blue",
            1.0: "green",
            2.0: "orange",
            3.0: "red",
        }
        color = class_color_map.get(prediction, "black")  # Default to black if class not found

        # Line style based on test/train split
        linestyle = "--" if is_test else "-"

        # Correctness information for the label
        correctness_label = "Correct" if correct else "Incorrect"

        # Highlight in the first column plot
        axs[0].plot(
            bead_data_indices,
            raw_data.iloc[bead_data_indices, 0],
            color=color,
            linestyle=linestyle,
            label=f"Bead {bead_number} (Class {prediction}, {correctness_label})",
        )

        # Highlight in the second column plot
        axs[1].plot(
            bead_data_indices,
            raw_data.iloc[bead_data_indices, 1],
            color=color,
            linestyle=linestyle,
            label=f"Bead {bead_number} (Class {prediction}, {correctness_label})",
        )

    # Add legends
    axs[0].legend()
    axs[1].legend()

    # Show the plots
    st.pyplot(fig)

# Streamlit App
def main():
    st.title("Bead Data Plotter with Model Prediction Highlights")

    # Step 1: Load summary file
    st.sidebar.header("Upload Files")
    summary_file = st.sidebar.file_uploader("Upload Summary CSV", type=["csv"])
    data_dir = st.sidebar.text_input("Enter Data Directory Path", value="data/")

    if summary_file:
        # Load the summary data
        summary_df = load_summary_data(summary_file)

        # Step 2: Display available files
        available_files = summary_df["file"].unique()
        selected_file = st.selectbox("Select a CSV file to visualize", available_files)

        # Step 3: Plot selected file
        if selected_file:
            load_and_plot_csv_with_highlights(selected_file, summary_df, data_dir)

if __name__ == "__main__":
    main()

import pandas as pd
import argparse
import numpy as np
import os

def cmd_line_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-alpha", action='store', default='1', help="Area to the power of alpha in cost function")
    parser.add_argument("-beta", action='store', default='1', help="Delay to the power of beta in cost function")
    parser.add_argument("-i", action='store', required=True, help="Input folder name (include path if necessary)")
    return parser.parse_args()


def load_data(input_folder: str) -> pd.DataFrame:
    """Loads data from the qor_results.txt file within the input folder."""
    filepath = os.path.join(input_folder, 'qor_results.txt')
    return pd.read_csv(filepath, sep='\t')


def calculate_areas(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates area-related values."""
    df['Total_logic_block_area'] = (
        (df['Number_of_CLB_blocks'].clip(lower=0) * 2000) +
        (df['Number_of_DSP_blocks'].clip(lower=0) * 10500) +
        (df['Number_of_BRAM_blocks'].clip(lower=0) * 6000)
    ) * 29.53
    df['Total_used_area'] = df['Total_routing_block_area'] + df['Total_logic_block_area']
    return df


def calculate_geometric_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates geometric averages for area and delay."""
    df['geo_ave_area_arch'] = df.groupby('arch')['Total_used_area'].transform(lambda x: x.prod()**(1.0/len(x)))

    df['geo_ave_delay_arch'] = df.groupby('arch')['Critical_path_delay'].transform(
        lambda x: 0 if -1 in x.values else x.prod()**(1.0/len(x)))

    return df


def calculate_area_delay_model(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    """Calculates the area-delay model."""
    df['area_delay2_model_arch'] = (
        df['geo_ave_delay_arch']**(float(args.beta)) * df['geo_ave_area_arch']**(float(args.alpha))
    )
    return df


def save_results(df: pd.DataFrame, input_folder: str) -> None:
    """Saves the results to CSV and TSV files in the provided input folder."""
    parent_dir = os.path.dirname(os.path.abspath(input_folder))  # Get parent directory
    #parent_dir = Path(input_folder).parent
    output_txt = os.path.join(parent_dir, f'analyzed_qor_results.txt')
    output_csv = os.path.join(parent_dir, f'analyzed_qor_results.csv')

    df.to_csv(output_txt, sep='\t', index=False)
    df.to_csv(output_csv, sep=',', index=False)

def main():
    args = cmd_line_args()
    df = load_data(args.i)  
    df = calculate_areas(df)
    df = calculate_geometric_averages(df)
    df = calculate_area_delay_model(df, args)
    save_results(df, args.i)

if __name__ == "__main__":
    main()
    print ("Success: analyzed_qor_results files have been generated!")

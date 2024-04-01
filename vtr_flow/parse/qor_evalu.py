import pandas as pd
import argparse

def cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-alpha", action='store', default='1', help="Area to the power of alpha in cost function")
    parser.add_argument("-beta", action='store', default='1', help="Delay to the power of beta in cost function")
    args = parser.parse_args()
    return args

def load_data():
    df = pd.read_csv('qor_results.txt', sep='\t')
    return df

def calculate_areas(df):
    df['Total_logic_block_area'] = ((df['Number_of_CLB_blocks'].clip(lower=0) * 2000) + (df['Number_of_DSP_blocks'].clip(lower=0) * 10500) + (df['Number_of_BRAM_blocks'].clip(lower=0) * 6000)) * 29.53
    df['Total_used_area'] = df['Total_routing_block_area'] + df['Total_logic_block_area']
    return df

def calculate_geometric_averages(df):
    df['geo_ave_area_arch'] = df.groupby('arch')['Total_used_area'].transform(lambda x: x.prod()**(1.0/len(x)))
    df['geo_ave_delay_arch'] = df.groupby('arch')['Critical_path_delay'].transform(lambda x: x.prod()**(1.0/len(x)))
    return df

def calculate_area_delay_model(df, args):
    df['area_delay2_model_arch'] = df['geo_ave_delay_arch']**(float(args.alpha)) * df['geo_ave_area_arch']**(float(args.beta))
    return df

def save_results(df):
    df.to_csv('analyzed_qor_results.txt', sep='\t', index=False)
    df.to_csv('analyzed_qor_results.csv', sep=',', index=False)

def main():
    args = cmd_line_args()
    df = load_data()
    df = calculate_areas(df)
    df = calculate_geometric_averages(df)
    df = calculate_area_delay_model(df, args)
    save_results(df)

if __name__ == "__main__":
    main()

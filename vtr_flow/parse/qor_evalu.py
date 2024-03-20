import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('qor_results.txt', sep='\t')

# 1. Calculate Total_logic_block_area ()
df['Total_logic_block_area'] = ((df['Number_of_CLB_blocks'] * 2000) + (df['Number_of_DSP_blocks'] * 10500) + (df['Number_of_BRAM_blocks'] * 6000)) * 29.53

# Calculate Total_used_area
df['Total_used_area'] = df['Total_routing_block_area'] + df['Total_logic_block_area']

# Calculate geo_ave_area_arch
df['geo_ave_area_arch'] = df.groupby('arch')['Total_used_area'].transform(lambda x: x.prod()**(1.0/len(x)))

# Calculate geo_ave_delay_arch
df['geo_ave_delay_arch'] = df.groupby('arch')['Critical_path_delay'].transform(lambda x: x.prod()**(1.0/len(x)))

# Calculate geo_ave_area_circuit
df['geo_ave_area_circuit'] = df.groupby('circuit')['Total_used_area'].transform(lambda x: x.prod()**(1.0/len(x)))

# Calculate geo_ave_delay_circuit
df['geo_ave_delay_circuit'] = df.groupby('circuit')['Critical_path_delay'].transform(lambda x: x.prod()**(1.0/len(x)))

# Calculate area_delay2_model_arch
df['area_delay2_model_arch'] = df['geo_ave_delay_arch']**2 * df['geo_ave_area_arch']

# Calculate area_delay2_model_circuit
df['area_delay2_model_circuit'] = df['geo_ave_delay_circuit']**2 * df['geo_ave_area_circuit']

# Save the result to a new file
df.to_csv('analyzed_qor_results.txt', sep='\t', index=False)
# Save the result to a new file
df.to_csv('analyzed_qor_results.csv', sep=',', index=False)
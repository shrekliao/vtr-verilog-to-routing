# Push-Bottom Workflow
This document outlines the steps involved in the push-bottom workflow. The workflow consists of four main steps:

1. Generating the Architecture Files: We use a Python script to generate the architecture files from a template. The script takes a `values.txt` file as input, which contains the parameters for the architecture. Currently, we have a simple version that generates 54 different architectures for demonstration purposes.

    > python3 arch_render_march0315_dict.py -i arch_template_0402.xml -o ../arch/arch_gen/stratix.xml -p values.txt

2. Generating the Config File: We use another Python script to generate the config file. The script looks into the folders of Architecture and Benchmarks and adds all the file names into the config.txt. We use 18 benchmarks from VTR, resulting in 54 x 18 combinations.

    > python3 config_gen0331.py

3. Running VTR: Note that the current architecture is not optimized and is a patchwork from randomly existing architectures. As a result, some benchmarks may fail to run. You can see the result after Step 4 in the `analyzed_qor_results.csv` file.

    > python3 -u ../../scripts/run_vtr_task.py . -j 16

4. Evaluating Performance: We evaluate performance using a Python script. For the runs that fail, we exclude these results by assigning them a value of 0. Therefore, in the final comparison chart, we only compare the architectures that can successfully run with all provided benchmarks. Users can define `area**alpha * delay**beta` as they wish to evaluate the performance. Runtimes are also parsed.

    > python3 ../../../parse/qor_evalu.py -alpha 1 -beta 2

Please make sure you are in the target run folder when running these scripts.
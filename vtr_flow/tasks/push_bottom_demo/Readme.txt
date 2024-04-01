Push-bouttom workflow:

1. Architecture files  (Vendor provide)
python3 arch_render_march0315_dict.py -i stratix_template_0315.xml -o ../arch/arch_gen/stratix.xml -p values.txt

2. Generate Config file
python3 config_gen.py

3. Run VTR
python3 -u ../../scripts/run_vtr_task.py . -j 16

4. User define evaluate performance
python3 ../../../parse/qor_evalu.py

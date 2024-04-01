seed=(6 15 12 5 37)
init_temp=(0.9 0.8 0.7 0.6 0.5)
 Iterate over the list using a for loop
 for seed_val in "${seed[@]}"; do
     for temp in "${init_temp[@]}"; do
         echo -n "Seed: $seed_val"
         echo " init_temp: $temp"
         /packages/apps/vtr/8.0.0-git/vtr_flow/scripts/run_vtr_task.py part3_task/ -temp_dir part3_task/run_seed_${seed_val}_temp_${temp} -s --seed $seed_val -init_t $temp
     done
 done
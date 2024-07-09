import json
import os
import pickle
import random
import pandas as pd

merge = True
if merge:
    dataset1_path = 'data/dataset2/sqli_train.pkl'
    output_dir = 'wafamole_results/results_dataset_2/adv_payloads_train'
    output_files = [
        "adv_train_inf_svm_pl4_rs20_100rounds.pkl",
        "adv_train_log_reg_l1_pl4_rs20_100rounds.pkl",
        "adv_train_log_reg_l2_pl4_rs20_100rounds.pkl",
        "adv_train_rf_pl4_rs20_100rounds.pkl",
        "adv_train_svm_linear_l1_pl4_rs20_100rounds.pkl",
        "adv_train_svm_linear_l2_pl4_rs20_100rounds.pkl",
    ]

    with open(dataset1_path, 'rb') as f:
        dataset1 = pickle.load(f)

    for output_file in output_files:

        with open(os.path.join(output_dir, output_file), 'rb') as f:
            dataset2 = pickle.load(f)

        print(f"Processing {output_file}...")
        print("Length of dataset2:", len(dataset2))
        print("Length of dataset1:", len(dataset1))

       
        dataset1_copy = dataset1.copy()
        dataset1_copy[0:len(dataset2)] = dataset2
        
        merged_dataset = dataset1_copy
        #random.shuffle(merged_dataset)
        print("Length of merged dataset:", len(merged_dataset))
        
        output_path = os.path.join('data/dataset2', f'{output_file}')
        with open(output_path, 'wb') as f:
            pickle.dump(merged_dataset, f)

        print(f"Saved merged dataset to {output_path}")

    print("All datasets merged and saved successfully.")
    
else:
    
    json_files = [
        "wafamole_results/results_dataset_2/adv_payloads_test/adv_train_test_svm_linear_l1_pl4_rs20_100rounds.json",
        "wafamole_results/results_dataset_2/adv_payloads_test/adv_train_test_svm_linear_l2_pl4_rs20_100rounds.json"
    ]

    for json_file in json_files:
    
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        pkl_file = json_file.replace('.json', '.pkl')
        with open(pkl_file, 'wb') as file:
            pickle.dump(data, file)

        print(f"Converted {json_file} to {pkl_file}")

    
    
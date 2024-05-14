"""
This script is used to plot the ROC curves for the pretrained ML models and the ModSecurity WAF.
"""

import os
import matplotlib.pyplot as plt
import toml
import sys
import joblib
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import PyModSecurity
from src.data_loader import DataLoader
from src.extractor import ModSecurityFeaturesExtractor
from src.utils.plotting import plot_roc


if  __name__ == '__main__':
    settings         = toml.load('config.toml')
    crs_dir          = settings['crs_dir']
    crs_ids_path     = settings['crs_ids_path']
    models_path      = settings['models_path']
    figures_path     = settings['figures_path']
    dataset_path     = settings['dataset_path']
    paranoia_levels  = settings['params']['paranoia_levels']
    models           = settings['params']['models']
    other_models     = settings['params']['test_adv_models']
    penalties        = settings['params']['penalties']
    fig, axs         = plt.subplots(2, 2)
    zoom_axs         = dict()
    
    # LOADING DATASET PHASE
    print('[INFO] Loading dataset...')

    legitimate_train_path = os.path.join(dataset_path, 'legitimate_train.json')
    malicious_train_path  = os.path.join(dataset_path, 'malicious_train.json')
    legitimate_test_path  = os.path.join(dataset_path, 'legitimate_test.json')
    malicious_test_path   = os.path.join(dataset_path, 'malicious_test.json')
    adv_pl_paths = [
        os.path.join(dataset_path, f'adv_dsinf_svm_pl{pl}.json') for pl in range(1, 5)
    ]
    ms_adv_pl_paths = [
        os.path.join(dataset_path, f'adv_ds_ms_pl{pl}.json') for pl in range(1, 5)
    ]
    
    
    
    loader                = DataLoader(
        malicious_path  = malicious_train_path,
        legitimate_path = legitimate_train_path
    )    
    training_data = loader.load_data()

    loader = DataLoader(
        malicious_path  = malicious_test_path,
        legitimate_path = legitimate_test_path
    )    
    test_data = loader.load_data()
    
    #t = [0.5, 1, 2, 4, 5, 10]
    
#     color_mapping = {
#     0.5: 'red',
#     1: 'blue',
#     2: 'green',
#     4: 'purple',
#     5: 'orange',
#     10: 'brown'
# }
    for pl in paranoia_levels:
        print('[INFO] Extracting features for PL {}...'.format(pl))
        
        ms_adv_loader = DataLoader(
                    malicious_path=ms_adv_pl_paths[pl-1],
                    legitimate_path=legitimate_test_path
        )
        adv_inf_svm_loader = DataLoader(
                    malicious_path=adv_pl_paths[pl-1],
                    legitimate_path=legitimate_test_path
                )
                
        ms_adv_test_data = ms_adv_loader.load_data()
        adv_test_data = adv_inf_svm_loader.load_data()
        
        extractor = ModSecurityFeaturesExtractor(
            crs_ids_path = crs_ids_path,
            crs_path     = crs_dir,
            crs_pl       = pl
        )
    
        xts, yts = extractor.extract_features(test_data)
        ms_adv_xts, ms_adv_yts = extractor.extract_features(ms_adv_test_data)
        adv_xts, adv_yts = extractor.extract_features(adv_test_data)
        
        for model_name in other_models:
                print('[INFO] Evaluating {} model for PL {}...'.format(model_name, pl))
                    
                if model_name == 'modsec':
                    label_legend = 'ModSec'
                    color        = 'red'
                    ms_adv_label_legend = f'ModSec Model Adv PL{pl}'
                    ms_adv_settings = {'color': 'red', 'linestyle': 'dashed'}
                    waf = PyModSecurity(
                        rules_dir = crs_dir,
                        pl        = pl
                    )
                    y_scores = waf.predict(test_data['payload'])
                    ms_adv_y_scores = waf.predict(ms_adv_test_data['payload'])
                    
                    plot_roc(
                    yts, 
                    y_scores, 
                    label_legend       = label_legend,
                    ax                 = axs.flatten()[pl-1],
                    settings           = {'color': color},
                    plot_rand_guessing = False,
                    log_scale          = True,
                    update_roc_values  = True if pl == 1 else False,
                    include_zoom       = True,
                    zoom_axs           = zoom_axs,
                    pl                 = pl
                )
                    
                    plot_roc(
                    ms_adv_yts,
                    ms_adv_y_scores,
                    label_legend=ms_adv_label_legend,
                    ax=axs.flatten()[pl-1],
                    settings=ms_adv_settings,
                    plot_rand_guessing=False,
                    log_scale=True,
                    update_roc_values=False,
                    include_zoom=True,
                    zoom_axs=zoom_axs,
                    pl=pl
                )
        
                    
                elif model_name == 'infsvm':
                    label_legend  = f'InfSVM '
                    color = 'blue'
                    adv_label_legend = f'Adv InfSVM PL{pl}'
                    adv_settings = {'color': 'blue', 'linestyle': 'dashed'}
                    model         = joblib.load(
                        os.path.join(models_path, 'inf_svm_pl{}_t2.joblib'.format(pl))
                    )
                    y_scores     = model.decision_function(xts)
                    adv_y_scores = model.decision_function(adv_xts)
                    # print("coef\n",model.coef_)
                    # print("intercept\n",model.intercept_)
                    
                    plot_roc(
                        yts, 
                        y_scores, 
                        label_legend       = label_legend,
                        ax                 = axs.flatten()[pl-1],
                        settings           = {'color': color},
                        plot_rand_guessing = False,
                        log_scale          = True,
                        update_roc_values  = True if pl == 1 else False,
                        include_zoom       = True,
                        zoom_axs           = zoom_axs,
                        pl                 = pl
                    )
                    
                    
                    plot_roc(
                        adv_yts,
                        adv_y_scores,
                        label_legend=adv_label_legend,
                        ax=axs.flatten()[pl-1],
                        settings=adv_settings,
                        plot_rand_guessing=False,
                        log_scale=True,
                        update_roc_values=False,
                        include_zoom=True,
                        zoom_axs=zoom_axs,
                        pl=pl
                    )
            
                
    # Final global settings for the figure
    for idx, ax in enumerate(axs.flatten()):
        ax.set_title('PL {}'.format(idx+1), fontsize=20)
        ax.xaxis.set_tick_params(labelsize = 15)
        ax.yaxis.set_tick_params(labelsize = 15)
        ax.xaxis.label.set_size(20)
        ax.yaxis.label.set_size(20)

    handles, labels = axs.flatten()[0].get_legend_handles_labels()      
    
    fig.legend(
        handles, 
        labels,
        loc            = 'upper center',
        bbox_to_anchor = (0.5, -0.01),
        fancybox       = True,
        shadow         = True,
        ncol           = 6,
        fontsize       = 20
    )
    fig.set_size_inches(16, 10)
    fig.tight_layout(pad = 2.0)
    fig.savefig(
        os.path.join(figures_path, 'roc_curves_test_adv_t2.pdf'),
        dpi         = 600,
        format      = 'pdf',
        bbox_inches = "tight"
    )
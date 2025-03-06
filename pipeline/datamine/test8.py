import os
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Optional, Dict, Any
import shutil
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models.datamine.roles import ModuleArguments
from test1 import algo as extract_roles  
from test4 import process_common_args

def process_common_args(yaml_files: List[str]) -> List[ModuleArguments]:
    modules_args = defaultdict(list)

    def process_yaml_file(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

            for role in data:
                if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                    for task_file in role.get('role_root', {}).get('task_files', []):
                        for task in task_file.get('content', []):
                            for block in task.get('block', []):
                                action = block.get('action')
                                args = block.get('args', {})
                                if action and isinstance(args, dict):
                                    modules_args[action].extend(args.keys())

    for file_path in yaml_files:
        process_yaml_file(file_path)

    common_args_per_module = {module: list(set(args)) for module, args in modules_args.items()}
    
    return common_args_per_module


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    directory_path = os.path.join(config.output_directory, roles_dir_name)

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire '{directory_path}' n'existe pas.")

    yaml_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".yaml")]

    common_args_per_module = process_common_args(yaml_files)
    return common_args_per_module


def store_results(common_args_per_module: List[ModuleArguments], config, filename):
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    num_arguments = config.options.get("num_arguments", 7)  

    all_arguments = sorted(set(arg for args in common_args_per_module.values() for arg in args))

    arg_counter = Counter(arg for args in common_args_per_module.values() for arg in args)
    top_arguments = [arg for arg, _ in arg_counter.most_common(num_arguments)]

    module_arg_matrix = {module: {arg: 0 for arg in top_arguments} for module in common_args_per_module}

    for module, args in common_args_per_module.items():
        for arg in args:
            if arg in top_arguments:  
                module_arg_matrix[module][arg] = 1

    df = pd.DataFrame.from_dict(module_arg_matrix, orient="index")

    if df.shape[1] < 2:
        print("not enough")
        return

    correlation_matrix = df.corr().fillna(0)

    print("Matrice de corrélation des arguments :\n", correlation_matrix)

    correlation_csv_path = output_dir / "argument_correlation_matrix.csv"
    correlation_matrix.to_csv(correlation_csv_path)
    print(f" Matrice de corrélation enregistrée en CSV sous {correlation_csv_path}")

    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"Matrice de Corrélation des {num_arguments} Arguments les Plus Utilisés")

    correlation_image_path = output_dir / "argument_correlation_matrix.png"
    plt.savefig(correlation_image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Matrice de corrélation enregistrée sous {correlation_image_path}")  

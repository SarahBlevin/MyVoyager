import os
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from typing import List, Optional, Dict, Any
import shutil
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models.datamine.roles import LoopUsage
from test1 import algo as extract_roles  

import attr



def process_loop_usage(yaml_files: List[str]) -> List[LoopUsage]:
    loop_usage = defaultdict(lambda: [0, 0])  

    def process_yaml_file(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

            for role in data:
                if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                    for task_file in role.get('role_root', {}).get('task_files', []):
                        for task in task_file.get('content', []):
                            for block in task.get('block', []):
                                action = block.get('action')
                                if action:
                                    loop_usage[action][1] += 1
                                    if 'loop' in block:
                                        loop_usage[action][0] += 1

    for file_path in yaml_files:
        process_yaml_file(file_path)

    loop_percentage_per_module = {
        module: (usage[0] / usage[1] * 100 if usage[1] > 0 else 0)
        for module, usage in loop_usage.items()
    }

    return [LoopUsage(module=mod, loop_percentage=perc) for mod, perc in loop_percentage_per_module.items()]


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    directory_path = os.path.join(config.output_directory, roles_dir_name)

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire '{directory_path}' n'existe pas.")

    yaml_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".yaml")]

    loop_usage_results = process_loop_usage(yaml_files)

    store_results(loop_usage_results, config, "LoopUsageAnalysis")

    return loop_usage_results


def store_results(loop_usage_results: List[LoopUsage], config, filename):
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)
    num_modules = config.options.get("num_modules", 8)

    print("nnnnnnnnnnnnnuuuuumber of modules", num_modules)

    for loop_usage in loop_usage_results:
        loop_usage.dump(output_dir)

    print(f"Stockage temporaire terminé : {len(loop_usage_results)} fichiers JSON créés dans {output_dir}.")

    loop_usage_dict = {usage.module: usage.loop_percentage for usage in loop_usage_results}

    json_file_path = output_dir / "loop_usage_result.json"
    with open(json_file_path, "w") as f:
        json.dump({"data": loop_usage_dict}, f, indent=2, sort_keys=True)

    csv_file_path = output_dir / "loop_usage_percentage_per_module.csv"
    df = pd.DataFrame.from_dict(loop_usage_dict, orient='index', columns=['Loop Usage Percentage'])
    df.index.name = 'Module'
    df.to_csv(csv_file_path)

    print(f"Les résultats ont été sauvegardés dans '{json_file_path}' et '{csv_file_path}'.")

    top_loop_usage = sorted(loop_usage_dict.items(), key=lambda x: x[1], reverse=True)[:num_modules]

    if top_loop_usage:
        modules, percentages = zip(*top_loop_usage)
        plt.figure(figsize=(12, 8))
        sns.barplot(x=list(modules), y=list(percentages))
        plt.xticks(rotation=90)
        plt.xlabel("Modules")
        plt.ylabel("Loop Usage Percentage")
        plt.title(f"Top {num_modules} Modules Using Loops")
        plt.savefig(output_dir / f"top_{num_modules}_loop_usage.png", dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Graphique des {num_modules} modules les plus utilisés avec loops généré avec succès.")

    for file in output_dir.glob("*.json"):
        file.unlink()

    print("Tous les fichiers JSON temporaires ont été supprimés.")
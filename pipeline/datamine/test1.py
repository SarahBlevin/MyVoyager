

from collections import Counter, defaultdict
import csv
import os

import yaml

from models.datamine.roles import Module, MostUsedRoles


from typing import Optional, Dict, Any

import util

def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    """Go over each role and read the YAML files obtained from the previous stage."""
    num_modules = options.get("num_modules", 8) if options else 8

    roles_directory_path = os.path.join(config.output_directory, roles_dir_name)  
    modules_per_role = defaultdict(lambda: Counter())
    role_ids = []

    if not os.path.exists(roles_directory_path):
        raise FileNotFoundError(f"Roles directory '{roles_directory_path}' does not exist.")

    def process_yaml_file(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            inc = 1

            for role in data:
                if isinstance(role, dict):
                    role_id = role.get('role_id')
                    print(f"Traitement du rôle avec ID : {role_id}")
                    inc += 1
                    role_rev = role.get('role_rev')
                    task_files = role.get('role_root', {}).get('task_files', [])

                    if role_rev == "HEAD" or inc == len(data):
                        role_ids.append(role_id)

                        for task_file in task_files:
                            tasks = task_file.get('content', [])
                            for task in tasks:
                                for block in task.get('block', []):
                                    action = block.get('action')
                                    if action:
                                        modules_per_role[role_id][action] += 1
                else:
                    print(f"Fichier '{file_path}' à vérifier : {role}")
                    print(f"Nom du fichier qui pose problème : {file_path}")

    for filename in os.listdir(roles_directory_path):
        if filename.endswith(".yaml"):
            process_yaml_file(os.path.join(roles_directory_path, filename))

    role_counts = Counter(role_ids)
    duplicated_roles = {role_id: count for role_id, count in role_counts.items() if count > 1}

    if duplicated_roles:
        print("Rôles dupliqués détectés :", duplicated_roles)

    most_used_roles = []
    for role_id, actions in modules_per_role.items():
        modules = [Module(name=action, uses=count) for action, count in actions.items()]
        most_used_roles.append(MostUsedRoles(name=role_id, modules=modules))
    
    print(most_used_roles)
    return most_used_roles

    
def store_results(results, config, filename) -> None:
    num_modules = config.options.get("num_modules", 8)
    """Store the results of a stage in the dataset."""
    dataset_dir_path = os.path.join(config.output_directory, filename)
    os.makedirs(dataset_dir_path, exist_ok=True)

    modules_per_role = defaultdict(list)
    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]

    # Create a set of all unique modules
    all_modules = list(set(module for modules in modules_per_role.values() for module in modules))

    # Initialize the module usage matrix
    module_usage_matrix = {role_id: {module: 0 for module in all_modules} for role_id in modules_per_role}

    # Populate the matrix with counts
    for role_id, modules in modules_per_role.items():
        for module in modules:
            if module in all_modules:
                module_usage_matrix[role_id][module] += 1

    """
    # Write the matrix to a CSV file
    output_file = os.path.join(config.output_directory, filename, "modules_par_role.csv")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Role"] + all_modules)
        for role_id, module_counts in module_usage_matrix.items():
            writer.writerow([role_id] + [module_counts[module] for module in all_modules])
    
    print(f"Module usage matrix saved to {output_file}.")
    """
    # Calculate module usage and generate top 50 modules plot
    module_usage = {module: 0 for module in all_modules}
    for role_id, module_counts in module_usage_matrix.items():
        for module, count in module_counts.items():
            module_usage[module] += count

    sorted_usage = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)
    top_50_modules = sorted_usage[:num_modules]

    # Plot the top 50 modules
    modules, counts = zip(*top_50_modules)

    util.create_bar_chart(
        x_data=modules,
        y_data=counts,
        title=f"Top {num_modules} Most Used Modules",
        xlabel="Modules",
        ylabel="Usage Count",
        output_directory=config.output_directory,
        output_dataset_name = filename,
        output_filename=f"top_{num_modules}_modules.png",
        figsize=(12, 8),
    )

    # Delete the CSV file 
    """
    csv_file_path = os.path.join(config.output_directory, filename, "modules_par_role.csv")
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    """
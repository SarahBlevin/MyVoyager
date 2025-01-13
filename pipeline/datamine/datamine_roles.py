from collections import defaultdict, Counter
import csv
import os
import yaml
from models.structural.role import MultiStructuralRoleModel
from pipeline.extract.extract_structural_models import ExtractStructuralModels
from pipeline.base import ResultMap, Stage
from config import MainConfig
from models.datamine.roles import MostUsedRoles, Module

import util

class DatamineRoles(Stage[MostUsedRoles, MainConfig], requires=ExtractStructuralModels):

    dataset_dir_name = 'DatamineRoles'
    roles_dir_name = 'StructuralModels'  # Directory containing the roles YAML files

    def run(self, extract_structural_models: ResultMap[MultiStructuralRoleModel]) -> ResultMap[MostUsedRoles]:
        """Run the stage."""
        most_used_roles = self.algo(extract_structural_models)
        self.store_image_roles(most_used_roles)
        return ResultMap(most_used_roles)

    def report_results(self, results: ResultMap[MostUsedRoles]) -> None:
        """Report statistics on gathered roles."""
        print('--- Role Datamine ---')
        print(f'Extracted {len(results)} roles')

    def algo(self, models):
        """Go over each role and read the YAML files obtained from the previous stage."""
        roles_directory_path = os.path.join(self.config.output_directory, self.roles_dir_name)  
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

        return most_used_roles
    
    def store_image_roles(self, most_used_roles: ResultMap[MostUsedRoles]) -> None:
        """Store the results of a stage in the dataset."""
        dataset_dir_path = os.path.join(self.config.output_directory, self.dataset_dir_name)
        os.makedirs(dataset_dir_path, exist_ok=True)

        # Create a mapping of modules per role
        modules_per_role = defaultdict(list)
        for role in most_used_roles:
            modules_per_role[role.name] = [module.name for module in role.modules]

        # Create a set of all unique modules
        all_modules = list(set(module for modules in modules_per_role.values() for module in modules))

        # Initialize and populate the module usage matrix
        module_usage_matrix = {
            role_id: {module: 0 for module in all_modules} for role_id in modules_per_role
        }
        for role_id, modules in modules_per_role.items():
            for module in modules:
                module_usage_matrix[role_id][module] += 1

        # Calculate module usage directly in memory
        module_usage = {module: 0 for module in all_modules}
        for module_counts in module_usage_matrix.values():
            for module, count in module_counts.items():
                module_usage[module] += count

        # Sort the modules by usage and select the top 50
        sorted_usage = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)
        top_50_modules = sorted_usage[:50]

        # Extract module names and counts for plotting
        modules, counts = zip(*top_50_modules) if top_50_modules else ([], [])

        # Plot the top 50 modules
        util.create_bar_chart(
            x_data=modules,
            y_data=counts,
            title="Top 50 Most Used Modules",
            xlabel="Modules",
            ylabel="Usage Count",
            output_directory=self.config.output_directory,
            output_dataset_name=self.dataset_dir_name,
            output_filename="top_50_modules.png",
            figsize=(12, 8),
        )

        print(f"Top 50 most used modules plot saved to {self.config.output_directory}.")

        
        
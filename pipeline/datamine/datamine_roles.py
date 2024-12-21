from collections import defaultdict, Counter
import os
import yaml
from models.structural.role import MultiStructuralRoleModel
from pipeline.extract.extract_structural_models import ExtractStructuralModels
from pipeline.base import ResultMap, Stage
from config import MainConfig
from models.datamine.roles import MostUsedRoles, Module

class DatamineRoles(Stage[MostUsedRoles, MainConfig], requires=ExtractStructuralModels):

    dataset_dir_name = 'DatamineRoles'
    roles_dir_name = 'StructuralModels'  # Directory containing the roles YAML files

    def run(self, extract_structural_models: ResultMap[MultiStructuralRoleModel]) -> ResultMap[MostUsedRoles]:
        """Run the stage."""
        most_used_roles = self.algo(extract_structural_models)
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
                    
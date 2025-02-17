import importlib.util
import os
from typing import Any, Optional
from pipeline.base import Stage, ResultMap
from config import DatamineConfig

class DatamineStage(Stage[Any, DatamineConfig]):
    """
    Stage générique qui délègue l'algorithme à un script externe.

    Optionnellement (ou pas), le script peut définir une fonction `store_results` pour gérer le stockage.
    """

    dataset_dir_name = 'Datamine'

    def run(self) -> ResultMap[Any]:
        """

        :param algo_script_path: Chemin vers le script Python de l'algorithme.
        :param needs_data: Booléen indiquant si l'algorithme nécessite des données.
        :param data: Les données à transmettre à l'algorithme (si besoin).
        :return: Un ResultMap contenant le résultat de l'algorithme.
        """
    
        spec = importlib.util.spec_from_file_location("external_algo", self.config.path)
        external_algo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(external_algo)

        if not hasattr(external_algo, "algo"):
            raise AttributeError("Le script de l'algorithme doit contenir une fonction 'run_algo'.")

        # Exécuter l'algorithme en fonction du paramètre needs_data 
        if self.config.options:
            result = external_algo.algo(self.config, "StructuralModels", self.config.options)
        else:
            result = external_algo.algo(self.config, "StructuralModels")

        filename = os.path.basename(self.config.path)

        # L'idée est de checker si mon script externe contient une fonction store_result. 
        # De sorte, nous n'aurons pas toujours besoin de lancer certains algorithmes (gain de temps et d'energie) 
        output = os.path.join(self.dataset_dir_name, filename)
        if hasattr(external_algo, "store_results"):
            external_algo.store_results(result, self.config, output)

        return None

    def report_results(self, results: ResultMap[Any]) -> None:
        print("Résultats de l'algorithme :")
        print(results)
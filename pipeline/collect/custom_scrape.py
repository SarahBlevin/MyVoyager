"""Pipeline segment to collect raw API page responses from Ansible Galaxy."""
from typing import Any, Dict, Iterator, List, Optional, Set, cast

import json
import os

from pathlib import Path

from tqdm import tqdm

from config import CustomScrapeConfig
from models.galaxy import GalaxyAPIPage
from pipeline.base import ResultMap, Stage
from services.galaxy import GalaxyAPI


API_URLS = {
    # 'namespaces': 'https://galaxy.ansible.com/api/v1/namespaces/',
    # 'platforms': 'https://galaxy.ansible.com/api/v1/platforms/',
    # 'provider_namespaces': 'https://galaxy.ansible.com/api/v1/provider_namespaces/',
    # 'repositories': 'https://galaxy.ansible.com/api/v1/repositories/',
    'roles': 'https://galaxy.ansible.com/api/v1/roles/',
    # 'role_search': 'https://galaxy.ansible.com/api/v1/search/roles/',
    # 'tags': 'https://galaxy.ansible.com/api/v1/tags/',
    # 'users': 'https://galaxy.ansible.com/api/v1/users/',
    # 'community_surveys': 'https://galaxy.ansible.com/api/v1/community_surveys/repository/',
    # 'content': 'https://galaxy.ansible.com/api/v1/content/',  # Mainly for more detailed quality scores.
}

PAGE_SIZES = {
    'roles': 250,
    'content': 100,
}


class CustomScrape(Stage[GalaxyAPIPage, CustomScrapeConfig]):
    """Discover roles to put in the dataset."""

    dataset_dir_name = 'CustomScrape'

    def run(self) -> ResultMap[GalaxyAPIPage]:
        """Run the stage."""
        all_results: List[GalaxyAPIPage] = []
        for name, url in API_URLS.items():
            pages = self.load_pages(name, url)
            all_results.extend(pages)
        
        return []


    def load_pages(self, page_name: str, page_url: str) -> List[GalaxyAPIPage]:
        cached_results = self.try_load_pages(page_name)
        if cached_results is not None:
            return cached_results

        api = GalaxyAPI()
        page_size = PAGE_SIZES.get(page_name, 500)
        it_pages = api.load_pages(page_name, page_url, page_size=page_size)
        pbar = tqdm(
                desc=f'Loading {page_name} pages', unit='pages', leave=False)
        results: List[GalaxyAPIPage] = []

        total_set = False
        roles_loaded = 0
        for page in it_pages:
            if self.config.max_roles is not None and roles_loaded >= self.config.max_roles:
                break  # Stop loading more pages if we reach the max roles, unless max_roles is None
            if not total_set:
                pbar.total = (cast(int, page.response['count']) // page_size) + 1
                total_set = True
            pbar.update(1)
            # Check how many roles are on this page and update the count
            if page.page_type == 'roles':
                roles_in_page = len(page.response.get('results', []))
                if self.config.max_roles is not None and roles_loaded + roles_in_page > self.config.max_roles:
                    # Trim the number of roles if we exceed max_roles
                    roles_to_load = self.config.max_roles - roles_loaded
                    page.response['results'] = page.response['results'][:roles_to_load]
                    roles_in_page = roles_to_load
                roles_loaded += roles_in_page
            results.append(page)

            # Stop processing if we've hit the role limit, unless max_roles is None
            if self.config.max_roles is not None and roles_loaded >= self.config.max_roles:
                break
        pbar.close()
        self.save_pages(results)
        return results

    
    def validate_and_filter(self, role, schema):
        """Filter the role object to keep only fields set to True in the schema."""
        filtered_role = {}

        for key, value in schema.items():
            if isinstance(value, dict):  # Handle nested objects (e.g., summary_fields)
                filtered_subsection = self.validate_and_filter(role.get(key, {}), value)
                if filtered_subsection:  # Only add non-empty subsections
                    filtered_role[key] = filtered_subsection
            elif value is True and key in role:  # Only keep explicitly set True fields
                filtered_role[key] = role[key]

        return filtered_role


    def save_pages(self, results: List[GalaxyAPIPage]) -> None:
        """Save filtered API responses to the output directory."""
        dataset_dir_path = self.config.output_directory / self.dataset_dir_name
        os.makedirs(dataset_dir_path, exist_ok=True)

        # Load the schema to determine which fields to keep
        with open(self.config.schema, "r") as schema_file:
            schema = json.load(schema_file)

        for page in results:
            # Filter the results based on the schema
            filtered_results = [
                self.validate_and_filter(role, schema)
                for role in page.response.get("results", [])
            ]

            # Remove empty results
            filtered_results = [role for role in filtered_results if role]

            # Construct the filtered page content
            filtered_page_content = {
                "count": len(filtered_results),
                "results": filtered_results,
            }

            # Save the filtered JSON
            fpath = dataset_dir_path / f'{page.page_type}_{page.page_num}.json'
            print(fpath)
            fpath.write_text(json.dumps(
                    filtered_page_content, sort_keys=True, indent=2))
    
        self.report_result(results)

    def try_load_pages(self, page_name: str) -> Optional[List[GalaxyAPIPage]]:
        dataset_dir_path = self.config.output_directory / self.dataset_dir_name
        existing_files = list(dataset_dir_path.glob(f'{page_name}_*.json'))
        if not existing_files:
            return None

        cached_results = []
        for file in existing_files:
            comps = file.stem.split('_')
            file_type = '_'.join(comps[:-1])
            page_num = int(comps[-1])
            cached_results.append(
                    GalaxyAPIPage.load(f'{file_type}/{page_num}', file))

        return cached_results
    
    def report_results(self, results):
        """Report the results."""

    def report_result(self, results: ResultMap[GalaxyAPIPage]) -> None:
        """Report statistics on loaded pages."""
        print('--- Custom Scrape ---')
        print(f'Loaded {len(results)} pages of API results')
"""Pipeline segment to collect raw API page responses from Ansible Galaxy."""
from typing import Any, Dict, Iterator, List, Optional, Set, cast

import json
import os

from pathlib import Path

from tqdm import tqdm

from config import GalaxyScrapeConfig
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


class GalaxyScrape(Stage[GalaxyAPIPage, GalaxyScrapeConfig]):
    """Discover roles to put in the dataset."""

    dataset_dir_name = 'GalaxyScrape'

    def run(self) -> ResultMap[GalaxyAPIPage]:
        """Run the stage."""
        all_results: List[GalaxyAPIPage] = []
        for name, url in API_URLS.items():
            pages = self.load_pages(name, url)
            all_results.extend(pages)

        # Might happen that some roles in the role page fail to load because
        # of 500 Internal Server Error at Galaxy side. Can't fix this. The
        # role page includes more information though, and we've got both the
        # role search and the roles themselves. Any roles in the search page
        # that aren't present in the role pages need to be loaded separately
        # too. We'll give these incremental page numbers.
        all_results = self.import_missing_roles(all_results)
        return ResultMap(all_results)


    def import_missing_roles(self, results: List[GalaxyAPIPage]) -> List[GalaxyAPIPage]:
        role_ids: Set[int] = set()
        role_search_ids: Set[int] = set()
        highest_role_page_num = 0

        max_roles = self.config.max_roles
        roles_loaded = 0

        for page in results:
            if page.page_type == 'roles':
                highest_role_page_num = max(
                        highest_role_page_num, page.page_num)
                highest_role_page_num = max(highest_role_page_num, page.page_num)
                for role in cast(List[Dict[str, Any]], page.response['results']):
                    # Stop if we've already loaded the max number of roles, unless max_roles is None
                    if max_roles is not None and roles_loaded >= max_roles:
                        break
                    role_ids.add(role['id'])
                    roles_loaded += 1  # Increment roles loaded

            if page.page_type == 'role_search':
                for role in cast(List[Dict[str, Any]], page.response['results']):
                    # Stop if we've already loaded the max number of roles, unless max_roles is None
                    if max_roles is not None and roles_loaded >= max_roles:
                        break
                    role_search_ids.add(role['id'])
                    roles_loaded += 1  # Increment roles loaded
            # Exit if we've hit the max role count, unless max_roles is None
            if max_roles is not None and roles_loaded >= max_roles:
                break
        missing_ids = role_search_ids - role_ids

        remaining_roles = max_roles - roles_loaded if max_roles is not None else float('inf')
        if max_roles is None:
            # If max_roles is None, no limit, import all missing roles
            missing_ids = list(missing_ids)
        else:
            # If max_roles is specified, limit the number of roles
            remaining_roles = max_roles - roles_loaded
            missing_ids = list(missing_ids)[:remaining_roles] if remaining_roles > 0 else []

        new_pages: List[Any] = []
        api = GalaxyAPI()

        for role_id in tqdm(missing_ids, desc='Loading missing roles'):
            if max_roles is not None and roles_loaded >= max_roles:  # Check again just in case
                break
            role_page = api.load_role(role_id)
            if role_page is not None:
                new_pages.append(role_page)
                roles_loaded += len(role_page.response.get('results', []))  # Increment based on new roles loaded

        # Add the new pages with missing roles to the results
        page_content = {'results': new_pages}
        results.append(GalaxyAPIPage(
                'roles', highest_role_page_num + 1, json.dumps(page_content)))

        return results


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

    def save_pages(self, results: List[GalaxyAPIPage]) -> None:
        dataset_dir_path = self.config.output_directory / self.dataset_dir_name
        os.makedirs(dataset_dir_path, exist_ok=True)
        for page in results:
            page.dump(dataset_dir_path)

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

    def report_results(self, results: ResultMap[GalaxyAPIPage]) -> None:
        """Report statistics on loaded pages."""
        print('--- Galaxy Scrape ---')
        print(f'Loaded {len(results)} pages of API results')
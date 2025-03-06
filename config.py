"""Configurations."""

from pathlib import Path

import click
import json

from util.config import Config, Option

from typing import Any, Dict, Optional


class MainConfig(Config):
    """Global configurations for all commands."""

    report: Option[bool] = Option(
            'Output a report after a task has completed.', default=False)
    progress: Option[bool] = Option(
            'Print the progress of a task.', default=False)
    dataset: Option[str] = Option(
            'The name of the dataset to create/use', final=True)
    output: Option[Path] = Option(
            'Output directory', click_type=click.Path(
                file_okay=False, dir_okay=True, writable=True,
                resolve_path=True),
            converter=lambda p: Path(str(p)),
            default=Path('data'), final=True)
    force: Option[bool] = Option(
            'Force regeneration of cached results', default=False)
    delete: Option[bool] = Option(
                'Delete the output directory before running', default=False)

    @property
    def output_directory(self) -> Path:
        """Get the output directory."""
        return self.output / self.dataset

class GalaxyScrapeConfig(MainConfig):
    """Configuration for galaxy scraping."""

    # New option to limit the number of roles imported
    max_roles: Option[int] = Option(
        '--max-roles', 
        default=None,  # Default to None to indicate no limit
        required=False,
    )

class CustomScrapeConfig(MainConfig):
    """Configuration for custom scraping."""

    # New option to limit the number of roles imported
    max_roles: Option[int] = Option(
        '--max-roles', 
        default=None,  # Default to None to indicate no limit
        required=False,
    )

    schema: Option[Path] = Option(
    '--schema',
    click_type=click.Path(exists=True, readable=True, resolve_path=True),
    converter=Path,  # Explicitly converts input to a Path object
    required=True)



class ExtractRoleMetadataConfig(MainConfig):
    """Configuration for role metadata extraction."""

    count: Option[int] = Option('Top number of roles to keep', required=False)


class CloneConfig(MainConfig):
    """Configuration for cloning."""

    resume: Option[bool] = Option(
            'Resuming cloning from a previous run.', default=True)


class ExtractStructuralModelsConfig(MainConfig):
    """Configuration for structural model extraction."""

    commits: Option[bool] = Option(
            'Extract a structural model for each commit. If disabled, extracts for semantic versions only.', default=False)
     

class DatamineConfig(MainConfig):
    """Configuration for datamining."""

    
    options: Option[Dict[str, Any]] = Option(
        'Options à passer au script d’algorithme sous format JSON',
        default={},
        required=False,
        click_type=str, 
        converter=lambda x: json.loads(x) if x else {}  # j ai modifié options pour que ca marche ceci convertit le json en dict
    )
    
    path: Option[Path] = Option(
        'Path to the algorithm script', click_type=click.Path(exists=True, readable=True, resolve_path=True),
        converter=Path, required=True)


# Voyager++

Voyager++ is an advanced tool for collecting and analyzing datasets of Ansible roles from Ansible Galaxy. It builds on the original Voyager tool by Ruben Opdebeeck, addressing obsolescence and dependencies while introducing a datamining stage for deeper insights into role version histories. Designed for research projects, such as For-CoaLa, Voyager++ enables flexible data collection, repository analysis, and structural evolution tracking.

## Features

- **Data Collection**: Scrapes Ansible Galaxy for role information.
- **Metadata Extraction**: Extracts structured metadata from collected roles.
- **Repository Cloning**: Fetches role repositories for deeper analysis.
- **Structural Analysis**: Tracks changes in role configurations over versions.
- **Datamining**: Allows users to run custom analysis scripts.

## System Requirements

- **OS**: Linux/macOS/Windows
- **Python**: 3.8+
- **Dependencies**: Managed via [Poetry](https://python-poetry.org/)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/NotArobase/Voyager.git
   cd Voyager++
   ```
2. Install dependencies:
   ```sh
   poetry install
   ```
3. Verify installation:
   ```sh
   poetry shell
   python main.py --help
   ```

## Usage

### Basic Operations

- **Scrape data from Ansible Galaxy**: Collects role information from Ansible Galaxy. Limit the number of collected roles using the option --max-roles INT.
  ```sh
  python main.py --progress --report --dataset my_data galaxy-scrape
  ```
- **Custom scrape with user-defined schema**: Collects role data while filtering unnecessary attributes using a custom schema.
  ```sh
  python main.py --progress --report --dataset my_data custom-scrape --schema path/to/my_schema.json
  ```
- **Extract role metadata**: Extracts structured metadata (e.g., role dependencies, GitHub repositories) from the scraped dataset.
  ```sh
  python main.py --dataset my_data extract-role-metadata
  ```
- **Clone repositories**: Downloads the Git repositories for roles found in metadata.
  ```sh
  python main.py --dataset my_data clone
  ```
- **Extract Git metadata**: Retrieves commit history, branches, and tags from cloned repositories.
  ```sh
  python main.py --dataset my_data extract-git-metadata
  ```
- **Extract structural models** (for semantic version tags): Analyzes the structure of Ansible roles at each versioned release.
  ```sh
  python main.py --dataset my_data extract-structural-models
  ```
- **Extract structural models** (for each commit instead of versions): Captures structural changes in roles at every commit.
  ```sh
  python main.py --dataset my_data extract-structural-models --commits
  ```
- **Run a datamining script**: Executes an external analysis script on the dataset.
  ```sh
  python main.py --dataset my_data datamine-stage --path path/to/my_script.py
  ```

## Customization

Voyager++ supports easy customization for specific research needs:

- **Custom Scraping**: Define a JSON schema to filter collected data.
- **Datamining**: Plug in external analysis scripts. Said script must contain two specific functions (see user documentation).
  The tool comes with a number of "default" relevant datamining scripts, stored in Voyager/pipeline/datamine
- **Pipeline Extension**: Modify or add processing stages.

## Troubleshooting

- **Poetry not found?** Ensure it's installed and added to `PATH`.
- **Errors in metadata extraction?** Check dataset integrity and rerun the scraping step.

## Future Enhancements

- Frontend integration for better visualization.
- Containerization

For detailed documentation, visit the full [Voyager++ repository](https://github.com/NotArobase/Voyager.git) or read the full user documentation.

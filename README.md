# Voyager++

Voyager++ is an advanced tool for collecting and analyzing datasets of Ansible roles from Ansible Galaxy. It builds on the original Voyager, addressing obsolescence and dependencies while introducing a datamining stage for deeper insights into role version histories. Designed for research projects, such as For-CoaLa, Voyager++ enables flexible data collection, repository analysis, and structural evolution tracking.

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
   poetry run -- python main.py --help
   ```

## Usage

### Basic Operations

- **Scrape data from Ansible Galaxy**:
  ```sh
  poetry run -- python main.py --progress --report --dataset my_data galaxy-scrape
  ```
- **Extract metadata**:
  ```sh
  poetry run -- python main.py --dataset my_data extract-role-metadata
  ```
- **Clone repositories**:
  ```sh
  poetry run -- python main.py --dataset my_data clone
  ```
- **Run a datamining script**:
  ```sh
  poetry run -- python main.py --dataset my_data datamine-stage --path my_script.py
  ```

## Customization

Voyager++ supports easy customization for specific research needs:

- **Custom Scraping**: Define a JSON schema to filter collected data.
- **Datamining**: Plug in external analysis scripts.
- **Pipeline Extension**: Modify or add processing stages.

## Troubleshooting

- **Poetry not found?** Ensure it's installed and added to `PATH`.
- **Errors in metadata extraction?** Check dataset integrity and rerun the scraping step.

## Future Enhancements

- Frontend integration for better visualization.

For detailed documentation, visit the full [Voyager++ repository](https://github.com/NotArobase/Voyager.git).

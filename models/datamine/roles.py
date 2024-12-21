import json
from pathlib import Path
import attr
from models.base import Model
from typing import Sequence

@attr.s(auto_attribs=True)
class Module(Model):
    name: str
    uses: int

    @property
    def id(self) -> str:
        return self.name

@attr.s(auto_attribs=True)
class MostUsedRoles(Model):
    name: str
    modules: Sequence[Module]

    @property
    def id(self) -> str:
        return self.name

    def dump(self, directory: Path) -> Path:
        fpath = directory / f'{self.name}.json'
        # Create a dictionary to represent the object
        data = {
            "name": self.name,
            "modules": [attr.asdict(module) for module in self.modules]
        }
        # Write the data to the file
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath

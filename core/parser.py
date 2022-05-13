import yaml

import core.types


class Parser:
    def __init__(self, filename: str):
        self.filename = filename
 
    def parse_file(self) -> (
            dict[core.types.attribute, set[core.types.value]], list[dict[core.types.attribute, core.types.value]]
    ):
        with open(self.filename, 'r') as file:
            file_content = yaml.safe_load(file)
        for sec in ("domain", "instances"):
            if sec not in file_content:
                raise Exception("Lacking YAML section:", sec)
        list_domain = file_content["domain"]
        set_domain = {attribute: set(values) for attribute, values in list_domain.items()}
        return set_domain, file_content["instances"]

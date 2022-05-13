import core.types


class Instance:
    def __init__(self, content: dict[core.types.attribute, core.types.value], label: core.types.Label):
        self.content = content
        self.label = label

    def is_labeled(self) -> bool:
        return self.label is not core.types.Label.EMPTY

    def __repr__(self) -> str:
        acceptance_repr = " ".join(f"{attribute}:{value}" for attribute, value in self.content.items())
        return f"Label: {self.label.name} < {acceptance_repr} >"


class InstanceCreator:
    def __init__(self, domain: dict[core.types.attribute, set[core.types.value]]):
        self.domain = domain

    def create_instance(self, content: dict[core.types.attribute, core.types.value]) -> Instance:
        self._validate_content(content)
        label = core.types.Label.EMPTY
        if 'label' in content:
            content_label = content.pop('label')
            label = core.types.Label.POSITIVE if content_label else core.types.Label.NEGATIVE
        return Instance(content, label)

    def _validate_content(self, content: dict[core.types.attribute, core.types.value]):
        for attribute, value_set in self.domain.items():
            if attribute not in content:
                raise Exception(f"Invalid instance: attribute {attribute} in domain but not in the instance")
            if content[attribute] not in value_set:
                raise Exception(f"Invalid value for attribute {attribute}: {content[attribute]} not in domain")
        attribute_diff = set(content.keys()) - set(self.domain.keys())
        attribute_diff.discard('label')
        if attribute_diff:
            raise Exception(f"Invalid attributes for instance: {attribute_diff} not in domain")

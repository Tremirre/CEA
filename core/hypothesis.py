from __future__ import annotations

import copy
import itertools
import typing

import core.instance
import core.types


class Hypothesis:
    def __init__(self, attributes: typing.Iterable[core.types.attribute], strict_initialization=True):
        self.acceptance = {attribute: (None if strict_initialization else '?') for attribute in attributes}

    def does_accept_instance(self, instance: core.instance.Instance) -> bool:
        if self.is_unsatisfiable():
            return False
        for attribute, value in self.acceptance.items():
            if value == '?':
                continue
            if instance.content[attribute] != value:
                return False
        return True

    def is_unsatisfiable(self) -> bool:
        return None in set(self.acceptance.values())

    def is_consistent(self, instance: core.instance.Instance, should_accept: bool) -> bool:
        accepts_instance = self.does_accept_instance(instance)
        return accepts_instance is should_accept

    def is_more_general_then(self, hypothesis: Hypothesis):
        if self.acceptance.keys() != hypothesis.acceptance.keys():
            raise Exception("Cannot compare hypothesis of different domains!")
        if hypothesis.is_unsatisfiable():
            return True
        for own_value, against_value in zip(self.acceptance.values(), hypothesis.acceptance.values()):
            if own_value != '?' and own_value != against_value:
                return False
        return True

    def set_acceptance(self, new_acceptance: typing.Iterable[core.types.attribute]):
        self.acceptance = {attribute: new_val for attribute, new_val in zip(self.acceptance.keys(), new_acceptance)}

    def __repr__(self) -> str:
        acceptance_repr = " ".join(f"{attribute}:{value}" for attribute, value in self.acceptance.items())
        return f"< {acceptance_repr} >"

    def __hash__(self) -> int:
        pre_hashed = tuple(sorted(((key, val) for key, val in self.acceptance.items()), key=lambda t: t[0]))
        return hash(pre_hashed)


def get_minimally_generalized_hypothesis(hypothesis: Hypothesis, instance: core.instance.Instance) -> Hypothesis:
    if not instance.is_labeled() \
            or instance.label is core.types.Label.NEGATIVE \
            or hypothesis.does_accept_instance(instance):
        return hypothesis
    generalized_hypothesis = copy.deepcopy(hypothesis)
    for attribute, value in instance.content.items():
        if hypothesis.acceptance[attribute] in ('?', value):
            continue
        if hypothesis.acceptance[attribute] is None:
            generalized_hypothesis.acceptance[attribute] = value
            continue
        generalized_hypothesis.acceptance[attribute] = '?'
    return generalized_hypothesis


def get_stricter_consistent_hypotheses(
        hypothesis: Hypothesis,
        instance: core.instance.Instance,
        domain: dict[core.types.attribute, set[core.types.value]]
) -> set[Hypothesis]:
    if instance.label is not core.types.Label.NEGATIVE or hypothesis.is_consistent(instance, should_accept=False):
        return {hypothesis}
    stricter = set()
    for attribute, instance_value in instance.content.items():
        if hypothesis.acceptance[attribute] == '?':
            for attribute_value in domain[attribute]:
                if attribute_value == instance_value:
                    continue
                new_hypothesis = copy.deepcopy(hypothesis)
                new_hypothesis.acceptance[attribute] = attribute_value
                stricter.add(new_hypothesis)
    return stricter


def generate_all_hypotheses(domain: dict[core.types.attribute, set[core.types.value]]) -> set[Hypothesis]:
    result = set()
    if not domain:
        return result
    result.add(Hypothesis(domain.keys(), strict_initialization=True))
    whole_domain = tuple(domain.values())
    for attribute_domain in whole_domain:
        attribute_domain.add('?')
    all_hypothesis_acceptance = itertools.product(*whole_domain)
    for acceptance in all_hypothesis_acceptance:
        new_hypothesis = Hypothesis(domain.keys())
        new_hypothesis.set_acceptance(acceptance)
        result.add(new_hypothesis)
    return result


def pretty_print_hypotheses(hypotheses: typing.Iterable[Hypothesis],
                            attributes: typing.Iterable[core.types.attribute],
                            spacing: int = 10):
    if any(attributes != set(hypothesis.acceptance.keys()) for hypothesis in hypotheses):
        raise Exception("Cannot Pretty Print Hypothesis from different domains!")
    header = "INDEX".ljust(spacing)
    header += "".join(f"{attr}".ljust(spacing).upper() for attr in attributes)
    print(header)
    for index, hypothesis in enumerate(hypotheses):
        row = f"{index + 1}.".ljust(spacing)
        row += "".join(f"{hypothesis.acceptance[attr]}".ljust(spacing) for attr in attributes)
        print(row)

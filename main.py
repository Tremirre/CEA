import itertools

import core.algorithm
import core.hypothesis
import core.instance
import core.parser
import core.types

SETS_FOLDER = "training_sets"
SELECTED_SET = "cars.yaml"


def main():
    parser = core.parser.Parser(f"{SETS_FOLDER}/{SELECTED_SET}")
    domain, pre_instances = parser.parse_file()
    instance_creator = core.instance.InstanceCreator(domain)
    instance_pool = [
        instance_creator.create_instance(instance) for instance in pre_instances
    ]
    labeled_instances = [instance for instance in instance_pool if instance.is_labeled()]
    general, specific = core.algorithm.candidate_elimination(labeled_instances, domain)
    core.hypothesis.pretty_print_hypotheses(general, domain.keys())
    print(specific)


if __name__ == '__main__':
    main()

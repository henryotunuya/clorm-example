#!/usr/bin/env python

from clorm import monkey

monkey.patch()  # must call this before importing clingo

from clorm.clingo import Control

from clorm import ConstantStr, FactBase, Predicate, ph1_

from xclingo import XclingoControl, XclingoControlModelExplainer

ASP_PROGRAM = "encoding.lp"
XCLINGO_ANNOTATIONS = "annotations.lp"

# --------------------------------------------------------------------------
# Define a data model - we only care about defining the input and output
# predicates.
# --------------------------------------------------------------------------


class Driver(Predicate):
    name: ConstantStr


class Item(Predicate):
    name: ConstantStr


class Assignment(Predicate):
    item: ConstantStr
    driver: ConstantStr
    time: int


# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------

N_EXPLANATIONS = 0

def main():
    # Create a Control object that will unify models against the appropriate
    # predicates. Then load the asp file that encodes the problem domain.
    ctrl = Control(unifier=[Driver, Item, Assignment])
    ctrl.load(ASP_PROGRAM)

    # XclingoControl class does not use .load method, we need to add the string
    with open(ASP_PROGRAM, 'r') as infile:
        encoding_lp = infile.read()
    with open(XCLINGO_ANNOTATIONS, 'r') as infile:
        annotations_lp = infile.read()

    # Dynamically generate the instance data
    # drivers = [Driver(name=n) for n in ["Dave", "Morri", "Michael"]]
    drivers = [Driver(name=n) for n in ["dave", "morri", "michael"]]
    # items = [Item(name="item{}".format(i)) for i in range(1, 6)]
    items = [Item(name="item{}".format(i)) for i in range(1, 2)]
    instance = FactBase(drivers + items)

    # Add the instance data and ground the ASP program
    ctrl.add_facts(instance)
    ctrl.ground([("base", [])])

    # Generate a solution
    solution = None

    def on_model(model, instance):
        nonlocal solution
        solution = model.facts(atoms=True)

        model_explainer = XclingoControlModelExplainer(
            [],  # no solving args
            n_explanations=str(N_EXPLANATIONS),
        )

        model_explainer.add_to_explainer('base', [], encoding_lp)  # Adds the encoding
        model_explainer.add_to_explainer('base', [], instance.asp_str())  # Adds the instance
        model_explainer.add_to_explainer('base', [], annotations_lp)  # Adds the 

        model_explainer.add_model('base', [], solution.asp_str())  # Adds the model to be explained
        model_explainer.ground([("base", [])])  # Grounds the added model

        nmodel=0
        for x_model in model_explainer.solve():
            nmodel += 1
            print(f"Model to be explaiend:")
            print(x_model)
            nexpl = 0
            for graph_model in x_model.explain_model():
                nexpl += 1
                print(f"##Explanation: {nmodel}.{nexpl}")
                for sym in graph_model.show_trace:
                    e = graph_model.explain(sym)
                    if e is not None:
                        print(e)
            print(f"##Total Explanations:\t{nexpl}")
        if nmodel > 0:
            print(f"Models:\t{nmodel}")
            return False
        else:
            return True

    ctrl.solve(
        on_model=lambda model: on_model(model, instance)
    )
    if not solution:
        raise ValueError("No solution found")


# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
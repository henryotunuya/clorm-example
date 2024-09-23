#!/usr/bin/env python

from clorm import monkey

monkey.patch()  # must call this before importing clingo

from clorm.clingo import Control

from clorm import ConstantStr, FactBase, Predicate, ph1_

from xclingo import XclingoControl

ASP_PROGRAM = "encoding.lp"

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


def main():
    # Create a Control object that will unify models against the appropriate
    # predicates. Then load the asp file that encodes the problem domain.
    ctrl = Control(unifier=[Driver, Item, Assignment])
    ctrl.load(ASP_PROGRAM)

    # Dynamically generate the instance data
    drivers = [Driver(name=n) for n in ["Dave", "Morri", "Michael"]]
    items = [Item(name="item{}".format(i)) for i in range(1, 6)]
    instance = FactBase(drivers + items)

    # Add the instance data and ground the ASP program
    ctrl.add_facts(instance)
    ctrl.ground([("base", [])])
    

    # Generate a solution
    solution = None

    def on_model(model, instance, annotations):
        xclingo_control = XclingoControl()
        nonlocal solution
        solution = model.facts(atoms=True)

        program = you_get_it_from_facbase(instance)
        annotations = annotations

        xclingo_control.explain_model(program + annotations, model)

        print(solution)

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
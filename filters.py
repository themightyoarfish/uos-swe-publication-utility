from pybtex.database import Person
from itertools import chain


def get_person_filter(name):
    def filter_person(entry):
        people = entry.persons.values()
        for p in chain(*people):
            if name == ' '.join(chain(p.first_names, p.middle_names, p.last_names)):
                return True
        return False

    return filter_person


def get_mytype_filter(mytype):
    def filter_mytype(entry):
        if 'mytype' not in entry.fields:
            return False
        return entry.fields['mytype'].lower() == mytype.lower()

    return filter_mytype


def get_conjunction_filter(*fns):
    def logical_and(entry):
        for f in fns:
            if not f(entry):
                return False
        return True

    return logical_and

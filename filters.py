'''
Defines a few helpful functions for constructing filters on BibTeX entry. For
instance, different filters can be conjoined into a predicate so boilerplate is
reduced.

'''
from itertools import chain


def get_person_filter(name):
    '''
    :param str name: Name to filter for
    :return: A unary function rejecting entries whose ``persons`` field does
             not contain the given name. The match must be exact.
    :rtype: function
    '''
    def filter_person(entry):
        people = entry.persons.values()
        for p in chain(*people):
            if name == ' '.join(chain(p.first_names, p.middle_names, p.last_names)):
                return True
        return False

    return filter_person


def get_mytype_filter(mytype):
    '''
    :param str mytype: Name to filter for
    :return: A unary function rejecting entries whose ``mytype`` field does
             not equal the given value. The match is case-insensitive.
    :rtype: function
    '''
    def filter_mytype(entry):
        if 'mytype' not in entry.fields:
            return False
        return entry.fields['mytype'].lower() == mytype.lower()

    return filter_mytype


def get_conjunction_filter(*fns):
    '''
    :param list(function) fns: List of predicates
    :return: A unary function rejecting entries whose which do not satisfy all
             given predicates.
    :rtype: function
    '''
    def logical_and(entry):
        for f in fns:
            if not f(entry):
                return False
        return True

    return logical_and

'''Utility helpers for generating unique IDs.'''

import uuid


def generate_project_id() -> str:
    '''Return a new unique project identifier.'''
    return uuid.uuid4().hex

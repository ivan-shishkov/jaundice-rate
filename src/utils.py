import os.path
from contextlib import asynccontextmanager

from aionursery import Nursery, MultiError


@asynccontextmanager
async def create_handy_nursery():
    try:
        async with Nursery() as nursery:
            yield nursery
    except MultiError as e:
        if len(e.exceptions) == 1:
            raise e.exceptions[0]
        raise


def load_text_data(filepath):
    with open(filepath) as file_object:
        return file_object.read()


def get_charged_words(charged_dict_path='../charged_dict'):
    negative_words = (load_text_data(
        os.path.join(charged_dict_path, 'negative_words.txt'),
    )).splitlines()

    positive_words = (load_text_data(
        os.path.join(charged_dict_path, 'positive_words.txt'),
    )).splitlines()

    return negative_words + positive_words

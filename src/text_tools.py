import asyncio
import string

import pymorphy2
import pytest


def _clean_word(word):
    word = word.replace('«', '').replace('»', '').replace('…', '')
    word = word.strip(string.punctuation)
    return word


async def split_by_words(morph, text):
    """Разделяет текст на отдельные слова.

    Учитывает знаки пунктуации, регистр и словоформы, выкидывает предлоги.
    """
    words = []
    for word in text.split():
        cleaned_word = _clean_word(word)
        normalized_word = morph.parse(cleaned_word)[0].normal_form
        if len(normalized_word) > 2 or normalized_word == 'не':
            words.append(normalized_word)
        await asyncio.sleep(0)
    return words


@pytest.mark.asyncio
async def test_split_by_words():
    morph = pymorphy2.MorphAnalyzer()

    assert await split_by_words(morph, 'Во-первых, он хочет, чтобы') == ['во-первых', 'хотеть', 'чтобы']

    assert await split_by_words(morph, '«Удивительно, но это стало началом!»') == ['удивительно', 'это', 'стать', 'начало']


def calculate_jaundice_rate(article_words, charged_words):
    """Рассчитывает желтушность текста, принимает список "заряженных" слов и ищет их внутри article_words."""

    if not article_words:
        return 0.0

    found_charged_words = [word for word in article_words if word in set(charged_words)]

    score = len(found_charged_words) / len(article_words) * 100

    return round(score, 2)


def test_calculate_jaundice_rate():
    assert -0.01 < calculate_jaundice_rate([], []) < 0.01
    assert 33.0 < calculate_jaundice_rate(['все', 'аутсайдер', 'побег'], ['аутсайдер', 'банкротство']) < 34.0

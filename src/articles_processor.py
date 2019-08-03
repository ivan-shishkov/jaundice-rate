import asyncio
import time
import logging
from enum import Enum
from contextlib import contextmanager

import aiohttp
import pytest
import pymorphy2
from async_timeout import timeout

from adapters import SANITIZERS, ArticleNotFound
from text_tools import split_by_words, calculate_jaundice_rate
from utils import get_charged_words


class SanitizerNotImplemented(Exception):
    pass


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


@contextmanager
def work_time_counter(info_string=''):
    start_time = time.monotonic()
    try:
        yield
    finally:
        end_time = time.monotonic()
        work_time = end_time - start_time
        logging.info(f'{info_string} work time: {work_time:.3f} sec')


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def get_article_processing_results(status, url, words_count=None, score=None):
    return {
        'status': status.value,
        'url': url,
        'score': score,
        'words_count': words_count,
    }


def get_sanitized_article_text(article_url, html, plaintext=True):
    for site_name, sanitizer in SANITIZERS.items():
        if site_name in article_url:
            return sanitizer(html=html, plaintext=plaintext)

    raise SanitizerNotImplemented


async def process_article(
        session, article_url, morph, charged_words,
        max_pending_time_of_fetching_article=3,
        max_pending_time_of_splitting_by_words=3):
    try:
        async with timeout(max_pending_time_of_fetching_article):
            html = await fetch(session, article_url)

        article_text = get_sanitized_article_text(article_url, html)

        with work_time_counter(f'Splitting by words for article {article_url}'):
            async with timeout(max_pending_time_of_splitting_by_words):
                article_words = await split_by_words(morph, article_text)

    except aiohttp.ClientError:
        return get_article_processing_results(
            status=ProcessingStatus.FETCH_ERROR,
            url=article_url,
        )
    except (ArticleNotFound, SanitizerNotImplemented):
        return get_article_processing_results(
            status=ProcessingStatus.PARSING_ERROR,
            url=article_url,
        )
    except asyncio.TimeoutError:
        return get_article_processing_results(
            status=ProcessingStatus.TIMEOUT,
            url=article_url
        )

    jaundice_rate = calculate_jaundice_rate(article_words, charged_words)

    return get_article_processing_results(
        status=ProcessingStatus.OK,
        url=article_url,
        words_count=len(article_words),
        score=jaundice_rate,
    )


@pytest.mark.asyncio
async def test_process_article():
    morph = pymorphy2.MorphAnalyzer()
    charged_words = get_charged_words()

    async with aiohttp.ClientSession() as session:
        article_processing_results = await process_article(
            session=session,
            article_url='https://inosmi.ru/science/20190710/245445499.html',
            morph=morph,
            charged_words=charged_words,
        )
        assert article_processing_results['status'] == ProcessingStatus.OK.value

        article_processing_results = await process_article(
            session=session,
            article_url='https://inosmi.ru/science/20190710/245445498.html',
            morph=morph,
            charged_words=charged_words,
        )
        assert article_processing_results['status'] == ProcessingStatus.FETCH_ERROR.value

        article_processing_results = await process_article(
            session=session,
            article_url='https://example.com',
            morph=morph,
            charged_words=charged_words,
        )
        assert article_processing_results['status'] == ProcessingStatus.PARSING_ERROR.value

        article_processing_results = await process_article(
            session=session,
            article_url='https://inosmi.ru/science/20190710/245445499.html',
            morph=morph,
            charged_words=charged_words,
            max_pending_time_of_fetching_article=0.1,
        )
        assert article_processing_results['status'] == ProcessingStatus.TIMEOUT.value

        article_processing_results = await process_article(
            session=session,
            article_url='https://inosmi.ru/science/20190710/245445499.html',
            morph=morph,
            charged_words=charged_words,
            max_pending_time_of_splitting_by_words=0.1,
        )
        assert article_processing_results['status'] == ProcessingStatus.TIMEOUT.value

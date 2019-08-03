import asyncio
import logging
from functools import partial

import pymorphy2
from aiohttp import web, ClientSession

from articles_processor import process_article
from utils import create_handy_nursery, get_charged_words


async def handle_articles(request, morph, charged_words, max_urls_count=10):
    urls_string = request.query.get('urls')

    if not urls_string:
        return web.json_response(
            {'error': 'articles URLs not given'},
            status=400,
        )

    urls = urls_string.split(',')

    if len(urls) > max_urls_count:
        return web.json_response(
            {'error': f'too many URLs in request, should be {max_urls_count} or less'},
            status=400,
        )

    async with ClientSession() as session:
        async with create_handy_nursery() as nursery:
            tasks = [
                nursery.start_soon(
                    process_article(session, article_url, morph, charged_words),
                )
                for article_url in urls
            ]
            done_tasks, _ = await asyncio.wait(tasks)

    return web.json_response([task.result() for task in done_tasks])


def main():
    logging.basicConfig(level=logging.INFO)

    morph = pymorphy2.MorphAnalyzer()

    charged_words = get_charged_words()

    app = web.Application()
    app.add_routes(
        [
            web.get(
                path='/',
                handler=partial(
                    handle_articles,
                    morph=morph,
                    charged_words=charged_words,
                ),
            ),
        ],
    )
    web.run_app(app)


if __name__ == '__main__':
    main()

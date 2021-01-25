# encoding: utf-8
import os
import sys

from workflow import Workflow, web

GITEA_DOMAIN = os.environ.get('GITEA_DOMAIN', '')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')

repos_search_uri = '/api/v1/repos/search'


def search_repos(query):
    def _inner():
        url = '%s%s' % (GITEA_DOMAIN, repos_search_uri)
        return web.get(url, params={'q': query, 'access_token': ACCESS_TOKEN}).json()

    return _inner


def main(wf):
    query = sys.argv[-1] if len(sys.argv) > 1 else ''
    data = wf.cached_data(query, search_repos(query), max_age=300)
    for repo in data['data']:
        wf.add_item(
            repo['full_name'],
            subtitle='[Watchs: %s, Stars: %s, Forks: %s, Releases: %s] %s - %s' % (
                repo['watchers_count'],
                repo['stars_count'],
                repo['forks_count'],
                repo['release_counter'],
                repo['updated_at'][:10],
                repo['description'],
            ),
            arg=repo['html_url'],
            valid=True,
            icon='fork.png' if repo['fork'] else None,
            largetext=repo['full_name'],
            copytext=repo['full_name'],
        )
    wf.send_feedback()


if __name__ == '__main__':
    sys.exit(Workflow().run(main))

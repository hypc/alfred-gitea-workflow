# encoding: utf-8
import os
import sys
from datetime import datetime, timedelta

from workflow import Workflow, web

GITEA_DOMAIN = os.environ.get('GITEA_DOMAIN', '')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
LOCAL_TZ = os.environ.get('LOCAL_TZ', '+08:00')

LOCAL_TZ = (1 if LOCAL_TZ[0] == '+' else -1) * timedelta(hours=int(LOCAL_TZ[1:3]), minutes=int(LOCAL_TZ[4:6]))

apis = {
    'repos_search_uri': '/api/v1/repos/search'
}


def search_repos(query):
    def _inner():
        url = '%s%s' % (GITEA_DOMAIN, apis['repos_search_uri'])
        return web.get(url, params={
            'q': query, 'access_token': ACCESS_TOKEN, 'sort': 'updated', 'order': 'desc',
        }).json()

    return _inner


def format_datetime(dt_str):
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%XZ')
    local_dt = dt + LOCAL_TZ
    return local_dt.strftime('%Y-%m-%d %X')


def main(wf):
    query = sys.argv[-1] if len(sys.argv) > 1 else ''
    data = wf.cached_data(query, search_repos(query), max_age=300)
    for repo in data['data']:
        wf.add_item(
            repo['full_name'],
            subtitle='[Watchers: %s, Stars: %s, Forks: %s, Releases: %s] [%s] - %s' % (
                repo['watchers_count'],
                repo['stars_count'],
                repo['forks_count'],
                repo['release_counter'],
                format_datetime(repo['updated_at']),
                repo['description'],
            ),
            arg=repo['html_url'],
            valid=True,
            icon='fork.png' if repo['fork'] else None,
            largetext=repo['full_name'],
            copytext=repo['full_name'],
        )
    wf.add_item(
        'Go to the website',
        subtitle=GITEA_DOMAIN,
        arg='%s/explore/repos?sort=recentupdate&q=%s' % (GITEA_DOMAIN, query),
        valid=True,
    )
    wf.send_feedback()


if __name__ == '__main__':
    sys.exit(Workflow().run(main))

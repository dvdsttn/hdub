import os
import requests
from collections import Counter
from urllib.parse import urlparse, parse_qs

GITHUB_API_URL = 'https://api.github.com'
DEFAULT_API_HEADERS = {
    # set to preview for search api--- though ended up not using
    'Accept': 'application/vnd.github.mercy-preview+json'
}

# you can set GITHUB_OAUTH_TOKEN to a personal access token
# in the event that you end up hitting API rate limits
GITHUB_OAUTH_TOKEN = os.environ.get('GITHUB_OAUTH_TOKEN')
if GITHUB_OAUTH_TOKEN:
    DEFAULT_API_HEADERS['Authorization'] = f'token {GITHUB_OAUTH_TOKEN}'


class GithubAPIException(Exception):
    pass


def get_profile(profile):
    '''Takes a user profile and returns a dictionary containing information about their user account.'''
    repos = get_repos(profile)
    repo_stats = get_repo_stats(repos)
    starred_repos = get_starred_repos_count(profile)
    follower_count = get_follower_count(profile)
    commit_count = get_commit_count(profile, repos)

    result = {
        'public_source_repositories': repo_stats['source_repos'],
        'public_fork_repositories': repo_stats['forked_repos'],
        'watcher_count': repo_stats['watchers'],
        'follower_count': follower_count,
        'stars_received': repo_stats['stars_received'],
        'stars_given': starred_repos,
        'total_open_issues': repo_stats['open_issues'],
        'total_source_commit_count': commit_count,
        'total_account_size': repo_stats['size'],
        'languages': repo_stats['languages'],
        'language_count': len(repo_stats['languages']),
        'repo_topics': repo_stats['topics'],
        'repo_topics_count': len(repo_stats['topics']),
    }
    return result


def get_repos(profile):
    '''Take a profile and return a list of all repos for a given user profile.'''
    url = f"{GITHUB_API_URL}/users/{profile}/repos"
    repos = []
    while True:
        resp = requests.get(url, headers=DEFAULT_API_HEADERS)
        if resp.ok:
            repos.extend(resp.json())
        else:
            raise GithubAPIException(f'Error calling repos API. Status code: {resp.status_code}')
        try:
            # exit loop if we've already exhausted all content
            url = resp.links['next']['url']
        except KeyError:
            break
    return repos


def get_repo_stats(repos):
    '''Take a list of repos return a dictionary of aggregated stats for the repos.'''
    counts = Counter()
    languages = set()
    topics = set()

    for repo in repos:
        if repo['fork']:
            counts['forked_repos'] += 1
        else:
            # technically could split source/archived...
            counts['source_repos'] += 1

            # this is pretty costly for people with a large # of repos
            # could quickly exhaust the rate limits if you're not careful

        # can have open issues on forks
        counts['open_issues'] += repo['open_issues_count']

        # language can be a blank string, exclude in that case
        if repo['language']:
            languages.add(repo['language'].lower())

        topics.update(repo['topics'])

        counts['stars_received'] += repo['stargazers_count']
        counts['size'] += repo['size']
        counts['watchers'] += repo['watchers_count']

    # merge counts with other repo stats
    return {
        'forked_repos': counts['forked_repos'],
        'source_repos': counts['source_repos'],
        'open_issues': counts['open_issues'],
        'stars_received': counts['stars_received'],
        'size': counts['size'],
        'watchers': counts['watchers'],
        'languages': languages,
        'topics': topics,
    }


def get_commit_count(profile, repos):
    commit_count = 0
    for repo in repos:
        if not repo['fork']:
            commit_count += _get_repo_commit_count(profile, repo['name'])
    return commit_count


def _get_repo_commit_count(profile, repo):
    '''Takes a user profile and and repository and returns the number of commits to that repository.'''
    url = f'{GITHUB_API_URL}/repos/{profile}/{repo}/commits?per_page=1'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)

    if resp.ok is False:
        raise GithubAPIException(f'There was an error retrieving commit count. Status: {resp.status_code}')

    return parse_count_from_response(resp)


def get_starred_repos_count(profile):
    '''Takes a user profile name and returns the number of repos that user has starred.'''
    url = f'{GITHUB_API_URL}/users/{profile}/starred?per_page=1'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)

    if resp.ok is False:
        raise GithubAPIException(f'There was an error retrieving starred repo count. Status: {resp.status_code}')

    return parse_count_from_response(resp)


def get_follower_count(profile):
    '''Takes a user profile and returns the number of follwers they have'''
    url = f'{GITHUB_API_URL}/users/{profile}/followers?per_page=1'

    resp = requests.get(url, headers=DEFAULT_API_HEADERS)

    if resp.ok is False:
        raise GithubAPIException(f'There was an error retriving follower count. Status: {resp.status_code}')

    return parse_count_from_response(resp)


def parse_count_from_response(resp):
    '''Takes a response from the Github API and returns the total number of pages.
    '''
    # links will only be empty of 0 or 1 result
    if resp.links:
        parsed_url = urlparse(resp.links['last']['url'])
        # since we requested 1 resource per page take total pages as count
        count = int(parse_qs(parsed_url.query)['page'][0])
    else:
        # no last page to use, check length of result
        count = len(resp.json())
    return count

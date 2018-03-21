import requests
from collections import Counter

# https://developer.atlassian.com/bitbucket/api/2/reference/
BITBUCKET_API_URL = 'https://api.bitbucket.org/2.0'

# Didn't bother implementing auth because I didn't hit any rate limit.
DEFAULT_API_HEADERS = {
}


class BitbucketAPIException(Exception):
    pass


def get_profile(profile):
    '''Takes a user profile and returns a dictionary containing information about their user/team account.'''
    repos = get_repos(profile)
    repo_stats = get_repo_stats(repos)

    # Technically could call these functions during the get_repo_stats
    # function, but they need to make a network call for each repo and
    # the network IO is going to be way more time consuming than looping
    # through repos a few times, also this can make testing slightly more easy.
    open_issues = get_open_issue_count(profile, repos)
    commit_count = get_commit_count(profile, repos)
    watcher_count = get_watcher_count(profile, repos)

    profile_type = get_profile_type(profile)
    if profile_type == 'team':
        follower_count = get_team_follower_count(profile)
    elif profile_type == 'user':
        follower_count = get_user_follower_count(profile)
    else:
        raise BitbucketAPIException(f'Unsupported profile type: {profile_type}')

    result = {
        'public_source_repositories': repo_stats['sources'],
        'public_fork_repositories': repo_stats['forks'],
        'watcher_count': watcher_count,
        'follower_count': follower_count,
        'total_open_issues': open_issues,
        'total_source_commit_count': commit_count,
        'total_account_size': repo_stats['size'],
        'languages': repo_stats['languages'],
        'language_count': len(repo_stats['languages']),

        # unsupported by bitbucket API
        'stars_received': 0,
        'stars_given': 0,
        'repo_topics': set(),
        'repo_topics_count': 0,
    }
    return result


def get_repos(profile):
    '''Takes a profile and return a list of repositories for that profile'''
    url = f'{BITBUCKET_API_URL}/repositories/{profile}'
    repos = []

    while True:
        resp = requests.get(url, headers=DEFAULT_API_HEADERS)
        if resp.ok:
            response_json = resp.json()
            repos.extend(response_json['values'])
        else:
            raise BitbucketAPIException(f'Error calling repos API. Status code: {resp.status_code}')

        try:
            # exit while loop if there are no more pages
            url = response_json['next']
        except KeyError:
            break
    return repos


def get_repo_stats(repos):
    '''Take a list of repos return a dictionary of aggregated stats for the repos.'''
    counts = Counter()
    languages = set()
    for repo in repos:
        if 'parent' in repo:
            counts['forks'] += 1
        else:
            counts['sources'] += 1
        counts['size'] += repo['size']
        if repo['language']:
            languages.add(repo['language'].lower())
    return {
        'forks': counts['forks'],
        'size': counts['size'],
        'sources': counts['sources'],
        'languages': languages
    }


def get_open_issue_count(profile, repos):
    '''Takes a profile and list of repos and returns the count of open issues'''
    total_open_issues = 0
    for repo in repos:
        if repo['has_issues'] and 'parent' not in repo:
            total_open_issues += _get_repo_open_issues(profile, repo)
    return total_open_issues


def _get_repo_open_issues(profile, repo):
    '''Takes a profile and repo slug and returns the total count of open issues for that repo'''
    url = f'{BITBUCKET_API_URL}/repositories/{profile}/{repo["slug"]}/issues?q=state="open"'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)
    if resp.ok:
        return resp.json()['size']
    raise BitbucketAPIException(f'Error getting open issue count. Status code: {resp.status_code}')


def get_watcher_count(profile, repos):
    '''Take a profile and list of repos and return the sum of watchers for all repos'''
    watcher_count = 0
    for repo in repos:
        watcher_count += _get_repo_watcher_count(profile, repo)
    return watcher_count


def _get_repo_watcher_count(profile, repo):
    '''Take a profile and repo and return the number of watchers for that repo'''
    url = f'{BITBUCKET_API_URL}/repositories/{profile}/{repo["slug"]}/watchers'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)
    if resp.ok:
        return resp.json()['size']
    raise BitbucketAPIException(f'Error retrieving watcher count. Status code: {resp.status_code}')


def get_commit_count(profile, repos):
    total_commit_count = 0
    for repo in repos:
        if 'parent' not in repo:
            total_commit_count += _get_repo_commit_count(profile, repo)
    return total_commit_count


def _get_repo_commit_count(profile, repo):
    url = f'{BITBUCKET_API_URL}/repositories/{profile}/{repo["slug"]}/commits'
    commit_count = 0
    while True:
        resp = requests.get(url, headers=DEFAULT_API_HEADERS)
        if resp.ok:
            response_json = resp.json()
            commit_count += len(response_json['values'])
        else:
            raise BitbucketAPIException(f'Error calling repos API. Status code: {resp.status_code}')
        try:
            # exit loop if we've already exhausted all content
            url = response_json['next']
        except KeyError:
            break
    return commit_count


def get_profile_type(profile):
    '''Takes a profile and returns whether it is a user or team.'''
    url = f'{BITBUCKET_API_URL}/users/{profile}'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)
    if resp.ok:
        return 'user'

    url = f'{BITBUCKET_API_URL}/teams/{profile}'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)
    if resp.ok:
        return 'team'

    raise BitbucketAPIException('Count not determine profile type.')


def get_team_follower_count(profile):
    '''Takes a team profile and returns follower count.'''
    return _get_follower_count_by_type('teams', profile)


# It appears following users was deprecated....
def get_user_follower_count(profile):
    '''Takes a profile profile and returns follower count.'''
    return _get_follower_count_by_type('users', profile)


def _get_follower_count_by_type(_type, profile):
    '''Takes a profile type [team/user] and profile name and returns follower count.'''
    url = f'{BITBUCKET_API_URL}/{_type}/{profile}/followers'
    resp = requests.get(url, headers=DEFAULT_API_HEADERS)

    if resp.ok:
        return resp.json()['size']
    else:
        raise BitbucketAPIException(f'Error getting follower count. Status code: {resp.status_code}')

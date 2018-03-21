from github import get_profile as get_github_profile
from bitbucket import get_profile as get_bitbucket_profile
USERS = {}
BITBUCKET_PROFILES = {}
GITHUB_PROFILES = {}


class user:
    @staticmethod
    def create(username):
        '''Create a username.'''
        if username in USERS:
            return {'msg': f'user {username} already exists'}, 409
        USERS[username] = {
            'bitbucket': set(),
            'github': set()
        }
        return {'msg': f'user {username} created'}, 201

    @staticmethod
    def delete(username):
        '''Delete a username.'''
        try:
            USERS.pop(username)
            return {'msg': f'user {username} deleted successfully'}, 200
        except KeyError:
            return {'msg': f'user {username} not found'}, 404

    @staticmethod
    def get(username):
        '''Get all merged user profiles for username.'''
        if username in USERS:
            profiles = []
            for profile in USERS[username]['bitbucket']:
                profiles.append(BITBUCKET_PROFILES[profile])
            for profile in USERS[username]['github']:
                profiles.append(GITHUB_PROFILES[profile])

            merged_profile = {
                'follower_count': 0,
                'languages': set(),
                'public_fork_repositories': 0,
                'public_source_repositories': 0,
                'repo_topics': set(),
                'stars_given': 0,
                'stars_received': 0,
                'total_account_size': 0,
                'total_open_issues': 0,
                'total_source_commit_count': 0,
                'watcher_count': 0,
            }

            for profile in profiles:
                merged_profile['follower_count'] += profile['follower_count']
                merged_profile['public_fork_repositories'] += profile['public_fork_repositories']
                merged_profile['public_source_repositories'] += profile['public_source_repositories']
                merged_profile['stars_given'] += profile['stars_given']
                merged_profile['stars_received'] += profile['stars_received']
                merged_profile['total_account_size'] += profile['total_account_size']
                merged_profile['total_open_issues'] += profile['total_open_issues']
                merged_profile['total_source_commit_count'] += profile['total_source_commit_count']
                merged_profile['watcher_count'] += profile['watcher_count']

                merged_profile['repo_topics'] = merged_profile['repo_topics'].union(profile['repo_topics'])
                merged_profile['languages'] = merged_profile['languages'].union(profile['languages'])

            merged_profile['language_count'] = len(merged_profile['languages'])
            merged_profile['languages'] = sorted(merged_profile['languages'])
            merged_profile['repo_topics_count'] = len(merged_profile['repo_topics'])
            merged_profile['repo_topics'] = sorted(merged_profile['repo_topics'])

            return merged_profile, 200
        else:
            return {'msg': f'user {username} not found'}, 404


class bitbucket:
    @staticmethod
    def add(username, profile):
        '''Add a bitbucket profile to a username'''
        if username not in USERS:
            return {'msg': f'user {username} not found'}, 404

        # add profile to profiles always because api operations are expensive
        if profile not in BITBUCKET_PROFILES:
            BITBUCKET_PROFILES[profile] = get_bitbucket_profile(profile)

        for user_profile_name, profiles in USERS.items():
            if profile in profiles['bitbucket']:
                return {'msg': f'bitbucket profile {profile} already attached to {user_profile_name}'}, 409
        USERS[username]['bitbucket'].add(profile)
        return {'msg': f'added bitbucket profile {profile} to {username}'}, 201

    @staticmethod
    def delete(username, profile):
        '''Delete a bitbucket profile from a username.'''
        if username in USERS:
            try:
                USERS[username]['bitbucket'].remove(profile)
                return {'msg': f'removed {profile} from user {username}'}, 200
            except KeyError:
                return {'msg': f'{profile} not attached to user {username}'}, 404
        else:
            return {'msg': f'user {username} not found'}, 404


class github:
    @staticmethod
    def add(username, profile):
        '''Add a github profile to a username.'''
        if username not in USERS:
            return {'msg': f'user {username} not found'}, 404

        if profile not in GITHUB_PROFILES:
            GITHUB_PROFILES[profile] = get_github_profile(profile)

        for user_profile_name, profiles in USERS.items():
            if profile in profiles['github']:
                return {'msg': f'github profile {profile} already attached to {user_profile_name}'}, 409
        USERS[username]['github'].add(profile)
        return {'msg': f'added github profile {profile} to {username}'}, 201

    @staticmethod
    def delete(username, profile):
        '''Delete a github profile to a username.'''
        if username in USERS:
            try:
                USERS[username]['github'].remove(profile)
                return {'msg': f'removed {profile} from user {username}'}, 200
            except KeyError:
                return {'msg': f'{profile} not attached to user {username}'}, 404
        else:
            return {'msg': f'user {username} not found'}, 404

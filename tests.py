import github
import bitbucket
import db

from unittest.mock import Mock, patch
import unittest


class GithubAPITest(unittest.TestCase):
    @patch('github.get_repos')
    @patch('github.get_starred_repos_count')
    @patch('github.get_follower_count')
    @patch('github.get_commit_count')
    def test_get_profile(self, get_commit_count, get_follower_count, get_starred_repos_count, get_repos):
        get_commit_count.return_value = 12400
        get_follower_count.return_value = 24
        get_starred_repos_count.return_value = 666
        get_repos.return_value = [
            {
                'fork': False,
                'language': 'HTML',
                'open_issues_count': 0,
                'size': 255,
                'stargazers_count': 0,
                'topics': ['topic1'],
                'watchers_count': 4
            },
            {
                'fork': False,
                'language': 'JavaScript',
                'open_issues_count': 3,
                'size': 180,
                'stargazers_count': 4,
                'topics': ['topic1', 'topic2'],
                'watchers_count': 3
            },
            {
                'fork': True,
                'language': 'Python',
                'open_issues_count': 10,
                'size': 2410,
                'stargazers_count': 5,
                'topics': [],
                'watchers_count': 2
            }
        ]

        expected = {
            'follower_count': 24,
            'language_count': 3,
            'languages': set(['python', 'javascript', 'html']),
            'public_fork_repositories': 1,
            'public_source_repositories': 2,
            'repo_topics': set(['topic1', 'topic2']),
            'repo_topics_count': 2,
            'stars_given': 666,
            'stars_received': 9,
            'total_account_size': 2845,
            'total_open_issues': 13,
            'total_source_commit_count': 12400,
            'watcher_count': 9
        }

        profile = github.get_profile('someuserthatprobablydoesntexistintgithub')
        self.assertEqual(
            profile, expected
        )

    def test_get_repo_stats(self):
        # one of the only pure functions, wee easier to test!
        repos = [
            {
                'fork': False,
                'language': 'HTML',
                'open_issues_count': 0,
                'size': 255,
                'stargazers_count': 0,
                'topics': ['topic1'],
                'watchers_count': 4
            },
            {
                'fork': False,
                'language': 'JavaScript',
                'open_issues_count': 3,
                'size': 180,
                'stargazers_count': 4,
                'topics': ['topic1', 'topic2'],
                'watchers_count': 3
            },
            {
                'fork': True,
                'language': 'Python',
                'open_issues_count': 10,
                'size': 2410,
                'stargazers_count': 5,
                'topics': [],
                'watchers_count': 2
            }
        ]

        expected = {
            'forked_repos': 1,
            'source_repos': 2,
            'open_issues': 13,
            'size': 2845,
            'stars_received': 9,
            'watchers': 9,
            'topics': set(['topic2', 'topic1']),
            'languages': set(['python', 'javascript', 'html']),
        }

        stats = github.get_repo_stats(repos)
        self.assertEqual(stats, expected)

    def test_parse_count_from_response_with_links(self):
        mock_response = Mock()
        mock_response.links = {
            'last': {'url': 'https://api.github.com/?page=4'}
        }
        count = github.parse_count_from_response(mock_response)

        self.assertEqual(
            count,
            4,
            'parse_count_from_response should return last page number as an integer.'
        )

    def test_parse_count_from_response_without_links(self):
        mock_response = Mock()
        mock_response.links = {}
        mock_response.json = Mock(return_value=['list_item1', 'list_item2'])
        count = github.parse_count_from_response(mock_response)
        self.assertEqual(
            count,
            2,
            'parse_count_from_response with no links should return len of value returned from json() call'
        )


class BitbucketAPITest(unittest.TestCase):
    @patch('bitbucket.get_repos')
    @patch('bitbucket.get_open_issue_count')
    @patch('bitbucket.get_commit_count')
    @patch('bitbucket.get_watcher_count')
    @patch('bitbucket.get_profile_type')
    @patch('bitbucket.get_team_follower_count')
    def test_get_team_profile(
        self, get_team_follower_count, get_profile_type, get_watcher_count,
        get_commit_count, get_open_issue_count, get_repos
    ):
        get_repos.return_value = [
            {'language': 'java', 'size': 159815},
            {'language': 'go', 'size': 1241},
            {'language': 'python', 'parent': {'yep': True}, 'size': 19152657}
        ]
        get_open_issue_count.return_value = 27
        get_commit_count.return_value = 1337
        get_watcher_count.return_value = 666
        get_profile_type.return_value = 'team'
        get_team_follower_count.return_value = 100

        result = bitbucket.get_profile('thisprofilesurelydoesntexist')
        expected = {
            'follower_count': 100,
            'language_count': 3,
            'languages': set(['go', 'python', 'java']),
            'public_fork_repositories': 1,
            'public_source_repositories': 2,
            'repo_topics': set(),
            'repo_topics_count': 0,
            'stars_given': 0,
            'stars_received': 0,
            'total_account_size': 19313713,
            'total_open_issues': 27,
            'total_source_commit_count': 1337,
            'watcher_count': 666
        }

        self.assertEqual(
            result,
            expected
        )

    @patch('bitbucket.get_repos')
    @patch('bitbucket.get_open_issue_count')
    @patch('bitbucket.get_commit_count')
    @patch('bitbucket.get_watcher_count')
    @patch('bitbucket.get_profile_type')
    @patch('bitbucket.get_user_follower_count')
    def test_get_user_profile(
        self, get_user_follower_count, get_profile_type, get_watcher_count,
        get_commit_count, get_open_issue_count, get_repos
    ):
        get_repos.return_value = [
            {'language': 'java', 'size': 159815},
            {'language': 'go', 'size': 1241},
            {'language': 'c++', 'size': 2000},
            {'language': 'c++', 'size': 4000},
            {'language': 'python', 'parent': {'yep': True}, 'size': 19152657}
        ]
        get_open_issue_count.return_value = 14
        get_commit_count.return_value = 555
        get_watcher_count.return_value = 111
        get_profile_type.return_value = 'user'
        get_user_follower_count.return_value = 3

        result = bitbucket.get_profile('thisprofilesurelydoesntexist')
        expected = {
            'follower_count': 3,
            'language_count': 4,
            'languages': set(['go', 'python', 'java', 'c++']),
            'public_fork_repositories': 1,
            'public_source_repositories': 4,
            'repo_topics': set(),
            'repo_topics_count': 0,
            'stars_given': 0,
            'stars_received': 0,
            'total_account_size': 19319713,
            'total_open_issues': 14,
            'total_source_commit_count': 555,
            'watcher_count': 111
        }

        self.assertEqual(
            result,
            expected
        )

    def test_get_repo_stats(self):
        repos = [
            {'language': 'java', 'size': 159815},
            {'language': 'go', 'size': 1241},
            {'language': 'python', 'parent': {'yep': True}, 'size': 19152657}
        ]
        expected = {
            'forks': 1,
            'sources': 2,
            'languages': set(['python', 'go', 'java']),
            'size': 19313713
        }
        result = bitbucket.get_repo_stats(repos)
        self.assertEqual(
            result,
            expected
        )


class DBTest(unittest.TestCase):
    def setUp(self):
        db.USERS = {}
        db.BITBUCKET_PROFILES = {}
        db.GITHUB_PROFILES = {}

    def tearDown(self):
        db.USERS = {}
        db.BITBUCKET_PROFILES = {}
        db.GITHUB_PROFILES = {}

    def test_user_create(self):
        response, status_code = db.user.create('david')
        expected_users_dict = {'david': {'bitbucket': set(), 'github': set()}}

        self.assertEqual(response, {'msg': 'user david created'})
        self.assertEqual(status_code, 201)
        self.assertEqual(db.USERS, expected_users_dict)

        response, status_code = db.user.create('david')
        self.assertEqual(response, {'msg': 'user david already exists'})
        self.assertEqual(status_code, 409, 'db.user.create should return 409 if user already exists')

    def test_delete_user(self):
        db.user.create('david')
        expected_users_dict = {'david': {'bitbucket': set(), 'github': set()}}
        # sanity check that user was created
        self.assertEqual(db.USERS, expected_users_dict)

        response, status_code = db.user.delete('david')
        self.assertEqual(response, {'msg': 'user david deleted successfully'})
        self.assertEqual(status_code, 200)
        self.assertEqual(db.USERS, {})

        response, status_code = db.user.delete('david')
        self.assertEqual(response, {'msg': 'user david not found'})
        self.assertEqual(status_code, 404)

    @patch('db.get_bitbucket_profile')
    @patch('db.get_github_profile')
    def test_get_user(self, get_bitbucket_profile, get_github_profile):
        self.maxDiff = None
        get_github_profile.return_value = {
            'follower_count': 24,
            'language_count': 3,
            'languages': set(['python', 'javascript', 'html']),
            'public_fork_repositories': 1,
            'public_source_repositories': 2,
            'repo_topics': set(['topic1', 'topic2']),
            'repo_topics_count': 2,
            'stars_given': 666,
            'stars_received': 9,
            'total_account_size': 2845,
            'total_open_issues': 13,
            'total_source_commit_count': 12400,
            'watcher_count': 9
        }

        get_bitbucket_profile.return_value = {
            'follower_count': 100,
            'language_count': 3,
            'languages': set(['go', 'python', 'java']),
            'public_fork_repositories': 1,
            'public_source_repositories': 7,
            'repo_topics': set(),
            'repo_topics_count': 0,
            'stars_given': 0,
            'stars_received': 0,
            'total_account_size': 19313713,
            'total_open_issues': 27,
            'total_source_commit_count': 1337,
            'watcher_count': 666
        }
        expected = {
            'follower_count': 124,
            'language_count': 5,
            'languages': sorted(['go', 'python', 'java', 'javascript', 'html']),
            'public_fork_repositories': 2,
            'public_source_repositories': 9,
            'repo_topics': sorted(['topic1', 'topic2']),
            'repo_topics_count': 2,
            'stars_given': 666,
            'stars_received': 9,
            'total_account_size': 19316558,
            'total_open_issues': 40,
            'total_source_commit_count': 13737,
            'watcher_count': 675
        }

        db.user.create('david')
        db.bitbucket.add('david', 'BITBUCKET_ACCOUNT_THAT_DOESNT_EXIST')
        db.github.add('david', 'GITHUB_ACCOUNT_THAT_DOESNT_EXIST')
        response, status = db.user.get('david')
        self.assertEqual(response, expected)
        self.assertEqual(status, 200)

        response, status = db.user.get('doesnotexist')
        self.assertEqual(response, {'msg': 'user doesnotexist not found'})
        self.assertEqual(status, 404)

    @patch('db.get_bitbucket_profile')
    def test_bitbucket_add(self, get_bitbucket_profile):
        # obviously there isn't a guarantee that what you put into the
        # 'database' is going to be well formed... this breaks everything
        # fine for test stubs though
        get_bitbucket_profile.return_value = 'this_is_a_user_profile'
        db.user.create('david')
        db.user.create('chester')
        response, status = db.bitbucket.add('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'added bitbucket profile coolranchdoritos to david'})
        self.assertEqual(status, 201)

        response, status = db.bitbucket.add('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'bitbucket profile coolranchdoritos already attached to david'})
        self.assertEqual(status, 409)

        response, status = db.bitbucket.add('cheetos', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'user cheetos not found'})
        self.assertEqual(status, 404)

        response, status = db.bitbucket.add('chester', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'bitbucket profile coolranchdoritos already attached to david'})
        self.assertEqual(status, 409)

    @patch('db.get_bitbucket_profile')
    def test_bitbucket_delete(self, get_bitbucket_profile):
        get_bitbucket_profile.return_value = 'this_is_a_user_profile'
        db.user.create('david')
        db.bitbucket.add('david', 'coolranchdoritos')

        response, status = db.bitbucket.delete('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'removed coolranchdoritos from user david'})
        self.assertEqual(status, 200)

        response, status = db.bitbucket.delete('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'coolranchdoritos not attached to user david'})
        self.assertEqual(status, 404)

        response, status = db.bitbucket.delete('david', 'doesntexist')
        self.assertEqual(response, {'msg': 'doesntexist not attached to user david'})
        self.assertEqual(status, 404)

        response, status = db.bitbucket.delete('cheetos', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'user cheetos not found'})
        self.assertEqual(status, 404)

    @patch('db.get_github_profile')
    def test_add_github_profile(self, get_github_profile):
        get_github_profile.return_value = 'this_is_a_user_profile'
        db.user.create('david')
        db.user.create('chester')
        response, status = db.github.add('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'added github profile coolranchdoritos to david'})
        self.assertEqual(status, 201)

        response, status = db.github.add('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'github profile coolranchdoritos already attached to david'})
        self.assertEqual(status, 409)

        response, status = db.github.add('cheetos', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'user cheetos not found'})
        self.assertEqual(status, 404)

        response, status = db.github.add('chester', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'github profile coolranchdoritos already attached to david'})
        self.assertEqual(status, 409)

    @patch('db.get_github_profile')
    def test_delete_github_profile(self, get_github_profile):
        get_github_profile.return_value = 'this_is_a_user_profile'
        db.user.create('david')
        db.github.add('david', 'coolranchdoritos')

        response, status = db.github.delete('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'removed coolranchdoritos from user david'})
        self.assertEqual(status, 200)

        response, status = db.github.delete('david', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'coolranchdoritos not attached to user david'})
        self.assertEqual(status, 404)

        response, status = db.github.delete('david', 'doesntexist')
        self.assertEqual(response, {'msg': 'doesntexist not attached to user david'})
        self.assertEqual(status, 404)

        response, status = db.github.delete('cheetos', 'coolranchdoritos')
        self.assertEqual(response, {'msg': 'user cheetos not found'})
        self.assertEqual(status, 404)


if __name__ == '__main__':
    unittest.main()

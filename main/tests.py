from django.test import TestCase
from django.urls import reverse

class IndexViewTests(TestCase):
    def test_index_to_issue_list_redirect(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, '/issues/')

class IssueListViewTests(TestCase):
    fixtures = ['testdata.json']
    
    def test_statistics_bar(self):
        """
        Verify that statistics bar shows the correct data.
        """
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('admin:main_issue_changelist'))
        self.assertEqual(response.status_code, 200)
        expected_str = """
<div style="margin-bottom: 1.2em;">

  <p style="display: inline-block; padding-right: 2em;">Total issues: 5</p>

  <p style="display: inline-block; padding-right: 2em;">Number of open issues: 1</p>

  <p style="display: inline-block; padding-right: 2em;">Number of closed issues: 4</p>

  <p style="display: inline-block; padding-right: 2em;">Number of WIP issues: 0</p>

  <p style="display: inline-block; padding-right: 2em;">Min resolution time: 3 days 6 hours 18 minutes</p>

  <p style="display: inline-block; padding-right: 2em;">Max resolution time: 26 days 22 hours 58 minutes</p>

  <p style="display: inline-block; padding-right: 2em;">Average resolution time: 14 days 9 hours 26 minutes</p>

</div>
"""
        # TODO: use lxml for parsing and analyzing HTML structure
        self.assertIn(expected_str, response.rendered_content)

    def test_num_issues(self):
        """
        Verify that number of issues in the list is correct.
        """

class IssueEditViewTests(TestCase):
    fixtures = ['testdata.json']

    def test_no_delete_button(self):
        """
        Verify there is no delete button on the Issue edit page.
        """
        issue_id = 1
        self.client.login(username='admin', password='admin')
        change_url = reverse('admin:main_issue_change', args=(issue_id,))
        delete_url = reverse('admin:main_issue_delete', args=(issue_id,))
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(delete_url, response.rendered_content)

    def test_no_buttons_for_staff(self):
        """
        Verify that there are no edit buttons
        on the Issue edit page for staff user.
        """
        issue_id = 1
        self.client.login(username='staffuser1', password='staffuser1')
        change_url = reverse('admin:main_issue_change', args=(issue_id,))
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        # Simply checking there are no <input>-tags of type="submit"
        self.assertNotRegex(
            response.rendered_content, r'<input [^>\s]*type=["\']submit["\']')

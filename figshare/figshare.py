import os
import six
import json
from requests_oauthlib import OAuth1Session

consumer_key = 'XJCbpn5nHHDNW48NBMx0eg'
consumer_secret = 'gcxv78Aq6kBulp663LFgug'


class Figshare(object):
    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret):
        self.client = OAuth1Session(
            consumer_key, consumer_secret, access_token, access_token_secret)
        self.endpoint = 'http://api.figshare.com/v1/my_data'

    def article(self, article_id):
        response = self.client.get(self.endpoint + '/articles/%s' % article_id)
        return response.json()['items']

    def delete_article(self, article_id):
        response = self.client.delete(
            self.endpoint + '/articles/%s' % article_id)
        return json.loads(response.content)

    def articles(self, limit=None):
        """
        Parameters
        ----------

        limit : int or None
            If not None, then limit the number of articles returned.

        Returns
        -------
        Dict of {count: integer count of articles, items: dictionary
        representing each article}
        """
        # API only returns 10 results at a time, so keep asking for more pages
        # until we can't get any more...
        all_articles = []
        count = 0
        page = 1
        while True:
            if limit is not None and (len(all_articles) < limit):
                break
            data = {'page': page}
            response = self.client.get(
                self.endpoint + '/articles',
                params={'page': page}
            )
            # Keep the response around for debugging if needed; get a separate
            # results dict
            results = response.json()

            if results['count'] == 0:
                break

            all_articles.extend(results['items'])
            count += results['count']
            page += 1

        # Reconstruct the JSON dict in the same format returned by a single
        # response (with keys [count, items])
        assert count == len(all_articles)
        return {'count': count, 'items': all_articles}

    def create_article(self, title, description, defined_type='dataset'):
        response = self.client.post(
            self.endpoint + '/articles',
            data=json.dumps({'title': title,
                             'description': description,
                             'defined_type': defined_type,
                             }),
            headers={'content-type': 'application/json'})
        return response.content.json()

    def make_private(self, article_id):
        response = self.client.post(
            '%s/articles/%s/action/make_private' % (self.endpoint, article_id))
        return response.content.json()

    def update_article(self, article_id, title=None, description=None,
                       defined_type=None):
        data = {'title': title,
                'description': description,
                'defined_type': defined_type}
        data = dict((k, v) for k, v in data.items() if v is not None)
        headers = {'content-type': 'application/json'}
        response = self.client.put(
            '%s/articles/%s' % (self.endpoint, article_id),
            data=json.dumps(data), headers=headers)
        return json.loads(response.content)

    def upload_file(self, article_id, filepath_or_buffer):
        if isinstance(filepath_or_buffer, six.string_types):
            file = open(filepath_or_buffer, 'rb')
            own_handle = True
        else:
            file = filepath_or_buffer
            own_handle = False

        try:
            files = {'filedata': (os.path.basename(file.name), file)}
            response = self.client.put(
                '%s/articles/%s/files' % (self.endpoint, article_id),
                files=files)
            return json.loads(response.content)
        finally:
            if own_handle:
                file.close()

    def delete_file(self, article_id, file_id):
        response = self.client.delete(
            '%s/articles/%s/files/%s' % (self.endpoint, article_id, file_id))
        return response.content.json()

    def add_links(self, article_id, links):
        """
        Parameters
        ----------
        article_id : int or str

        links : str, or list of str
        """
        if isinstance(links, six.string_types):
            links = [links]
        article = self.article(article_id)
        existing_links = article['links']

        for link in links:
            if link in existing_links:
                raise ValueError("Link (%s) already added to article" % link)

            body = {'link': link}
            headers = {'content-type': 'application/json'}
            response = self.client.put(
                self.endpoint + '/articles/%s/links' % article_id,
                data=json.dumps(body), headers=headers)
            return json.loads(response.content)

    def versions(self, article_id):
        """
        Parameters
        ----------
        article_id : int or str

        Returns
        -------
        JSON reponse
        """
        return json.loads(
            self.client.get(
                self.endpoint + '/articles/%s/versions' % article_id).content
        )

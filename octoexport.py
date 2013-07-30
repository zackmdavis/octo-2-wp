# Copyright (C) 2013 Collin Donnell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import yaml
import re
import os
import unidecode
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts

POSTS_PATH = ''   # Path to your Octopress _posts folder
WP_ENDPOINT = ''  # URL for your Wordpress installations XML RPC endpoint
WP_USERNAME = ''  # Your Wordpress username
WP_PASSWORD = ''  # Your Wordpress password


def main():
    os.chdir(POSTS_PATH)
    client = Client(url=WP_ENDPOINT, username=WP_USERNAME, password=WP_PASSWORD)
    sent_count = 0

    for a_file in os.listdir("."):
        if a_file.endswith('.md') or a_file.endswith('.html') or a_file.endswith('.markdown'):
            print("Starting: " + a_file)
            post = create_post_from_file(a_file)
            publish_post_using_client(post, client)
            sent_count += 1
            print("Sent " + str(sent_count) + ": " + post.title)


def create_post_from_file(a_file):
    post = WordPressPost()
    file_content = get_content_for_file(a_file)
    match = yaml_match_from_post_data(file_content)
    yaml_data = extract_yaml_data_using_match(file_content, match)
    add_meta_info_from_yaml_to_post(yaml_data, post, a_file)
    post.content = file_content[match.end():].strip()
    return post


def publish_post_using_client(post, client):
    if isinstance(post, WordPressPost):
        client.call(posts.NewPost(post))


def get_content_for_file(a_file):
    stream = open(a_file, 'r')
    file_content = stream.read()
    stream.close()
    return file_content


def yaml_match_from_post_data(post_data):
    return re.search(r'^-{3}([\w\W]+?)(-{3})([\w\W])', post_data, re.MULTILINE)


def extract_yaml_data_using_match(post_data, match):
    yaml_match = match.group(1)
    front_matter = yaml.load(yaml_match)
    return front_matter


def add_meta_info_from_yaml_to_post(front_matter, post, filename):
    title = front_matter['title']
    post.title = title
    post.slug = slugify(title)
    if 'date' in front_matter:
        date_string = front_matter['date']
        if not isinstance(date_string, datetime):
            date_string = datetime.strptime(date_string[:16], '%Y-%m-%d  %H:%M')
        post.date = date_string
    else:
        # Attempt to get post date from filename
        post.date = datetime.strptime(filename[:10], '%Y-%m-%d')


def slugify(string):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', '-', string)


if __name__ == '__main__':
    main()

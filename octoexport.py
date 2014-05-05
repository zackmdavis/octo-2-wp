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
import markdown2
from collections import OrderedDict
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts

POSTS_PATH = ''   # Path to your Octopress _posts folder
WP_ENDPOINT = ''  # URL for your Wordpress installations XML RPC endpoint
WP_USERNAME = ''  # Your Wordpress username
WP_PASSWORD = ''  # Your Wordpress password
CONVERT_TO_HTML = False # Whether to convert Markdown to HTML


class OctoexportException(Exception):
    pass


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


def convert_post_to_html(content):
    return unicode(markdown2.markdown(content))


def create_post_from_file(a_file):
    post = WordPressPost()
    file_content = get_content_for_file(a_file)
    match = yaml_match_from_post_data(file_content)
    yaml_data = extract_yaml_data_using_match(file_content, match)
    add_meta_info_from_yaml_to_post(yaml_data, post, a_file)
    file_content = file_content[match.end():].strip()
    if CONVERT_TO_HTML:
        file_content = convert_image_tags(file_content)
        file_content = convert_post_to_html(file_content)
    post.content = file_content
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


# reference implementation: https://github.com/imathis/octopress/blob/fdf6af1d/plugins/image_tag.rb
def image_tag_dictionary(matchobject):
    attributes = ['class', 'src', 'width', 'height', 'title']
    img = OrderedDict([(group, match.strip())
           for group, match in sorted(matchobject.groupdict().items(), key=lambda x: attributes.index(x[0]))
           if match and group in attributes])
    alt_regex = re.compile('''(?:"|')(?P<title>[^"']+)?(?:"|')\s+(?:"|')(?P<alt>[^"']+)?(?:"|')''')
    alt_matchobject = alt_regex.search(img.get('title', ''))
    if alt_matchobject:
        img['title'] = alt_matchobject.group('title')
        img['alt'] = alt_matchobject.group('alt')
    else:
        img['alt'] = img['title'].replace('"', '&#34;') if img.get('title') else None
    img['class'] = img['class'].replace('"', '') if img.get('class') else None
    return img

def image_tag_render(matchobject):
    tag_dictionary = image_tag_dictionary(matchobject)
    if tag_dictionary:
        return "".join(["<img ",
                        " ".join('{0}="{1}"'.format(k, v)
                                 for k, v in tag_dictionary.items() if v), ">"])
    else:
        raise OctoexportException

def convert_image_tags(post_data):
    img_tag_regex = re.compile("{%\s*img\s+(?P<class>\S.*\s+)?(?P<src>(?:https?:\/\/|\/|\S+\/)\S+)(?:\s+(?P<width>\d+))?(?:\s+(?P<height>\d+))?(?P<title>\s+.+)?\s*%}")
    return img_tag_regex.sub(image_tag_render, post_data)


def slugify(string):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', '-', string)


if __name__ == '__main__':
    main()

import unittest
from octoexport import *

class TestImageTagConversion(unittest.TestCase):

    def test_convert_image_tags(self):
        # https://github.com/imathis/octopress/blob/fdf6af1d/plugins/image_tag.rb#L13
        examples = {"{% img /images/ninja.png %}": '<img src="/images/ninja.png">',
                    "{% img left half http://site.com/images/ninja.png Ninja Attack! %}": '<img class="left half" src="http://site.com/images/ninja.png" title="Ninja Attack!" alt="Ninja Attack!">',
                    '{% img left half http://site.com/images/ninja.png 150 150 "Ninja Attack!" "Ninja in attack posture" %}': '<img class="left half" src="http://site.com/images/ninja.png" width="150" height="150" title="Ninja Attack!" alt="Ninja in attack posture">'}
        for input_, output in examples.items():
            self.assertEqual(output, convert_image_tags(input_))

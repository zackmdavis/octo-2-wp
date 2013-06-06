# Octopress to Wordpress Migration Script

Read the contents of an Octopress `_posts` directory and adds them as **unpublished** posts to a Wordpress blog.

## Notes
* You should probably set up [virtualenv and virtualenvwrapper](http://mkelsey.com/2013/04/30/how-i-setup-virtualenv-and-virtualenvwrapper-on-my-mac/), set up an environment for the script and then install it's requirements using `pip install -r requirements.txt`. 
* Does not do any formatting of post content. You should probably have a Markdown plugin installed *before* running the script. If you want to send content as HTML to Wordpress, you can easily use pip to install a Markdown module and process the content.
* Makes no effort to retain Octopress categories.
* MIT licensed — no guarantee this won't screw anything up.

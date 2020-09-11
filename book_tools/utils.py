import re


def base_name(title):
    """ Clean human-readable book title."""
    # Convert to lower case
    title = title.lower()
    # Remove leading and trailing whitespace
    title = title.lstrip()
    title = title.rstrip()
    # Remove subtitle
    title = re.split(r"[:;]+", title)[0]
    # Remove 'the ' prefix (as it is not consistently used across lists)
    title[title.startswith('the ') and len('the '):]
    # Remove 'a ' prefix (as it is not consistently used across lists)
    title[title.startswith('a ') and len('a '):]
    return title

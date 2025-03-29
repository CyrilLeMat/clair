"""
Module for extracting and analyzing content from Confluence.
"""

from atlassian import Confluence
import yaml
import logging

def extract_and_analyze():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    if not config["confluence"]["enabled"]:
        logging.info("Confluence is not enabled, skipping")
        return

    confluence = Confluence(
        url=config["confluence"]["url"],
        username=config["confluence"]["username"],
        password=config["confluence"]["password"],
    )
    page_contents = extract(confluence)
    logging.info(f"Extracted {len(page_contents)} pages from Confluence")
    print(page_contents)
    # TODO: Preprocess and send for analysis
    pass


def extract(confluence: Confluence):
    # Get list of all pages in Confluence
    pages = confluence.get_all_pages()
    return pages

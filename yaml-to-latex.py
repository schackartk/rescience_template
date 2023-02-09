#!/usr/bin/env python3

"""
ReScience yaml to latex converter
Released under the BSD two-clauses licence
"""


def generate_latex_metadata(filename, article):
    """Generate a LaTeX file of the metadata from YAML"""
    abstract = article.abstract.replace("&", r"\&")

    content = (
        "% DO NOT EDIT - automatically generated from {filename}\n\n"
        "\\def \\codeURL{{{_.code.url}}}\n"
        "\\def \\codeDOI{{{_.code.doi}}}\n"
        "\\def \\codeSWH{{{_.code.swh}}}\n"
        "\\def \\dataURL{{{_.data.url}}}\n"
        "\\def \\dataDOI{{{_.data.doi}}}\n"
        "\\def \\editorNAME{{{_.editors[0].name}}}\n"
        "\\def \\editorORCID{{{_.editors[0].orcid}}}\n"
        "\\def \\reviewerINAME{{{_.reviewers[0].name}}}\n"
        "\\def \\reviewerIORCID{{{_.reviewers[0].orcid}}}\n"
        "\\def \\reviewerIINAME{{{_.reviewers[1].name}}}\n"
        "\\def \\reviewerIIORCID{{{_.reviewers[1].orcid}}}\n"
        "\\def \\dateRECEIVED{{{_.date_received}}}\n"
        "\\def \\dateACCEPTED{{{_.date_accepted}}}\n"
        "\\def \\datePUBLISHED{{{_.date_published}}}\n"
        "\\def \\articleTITLE{{{_.title}}}\n"
        "\\def \\articleTYPE{{{_.type}}}\n"
        "\\def \\articleDOMAIN{{{_.domain}}}\n"
        "\\def \\articleBIBLIOGRAPHY{{{_.bibliography}}}\n"
        "\\def \\articleYEAR{{{_.date_published.year}}}\n"
        "\\def \\reviewURL{{{_.review.url}}}\n"
        # "\\def \\articleABSTRACT{{{_.abstract}}}\n"
        "\\def \\articleABSTRACT{{{abstract}}}\n"
        "\\def \\replicationCITE{{{_.replication.cite}}}\n"
        "\\def \\replicationBIB{{{_.replication.bib}}}\n"
        "\\def \\replicationURL{{{_.replication.url}}}\n"
        "\\def \\replicationDOI{{{_.replication.doi}}}\n"
        "\\def \\contactNAME{{{_.contact.name}}}\n"
        "\\def \\contactEMAIL{{{_.contact.email}}}\n"
        "\\def \\articleKEYWORDS{{{_.keywords}}}\n"
        "\\def \\journalNAME{{{_.journal_info.name}}}\n"
        "\\def \\journalVOLUME{{{_.journal_info.volume}}}\n"
        "\\def \\journalISSUE{{{_.journal_info.issue}}}\n"
        "\\def \\articleNUMBER{{{_.journal_info.article_number}}}\n"
        "\\def \\articleDOI{{{_.journal_info.article_doi}}}\n"
        "\\def \\authorsFULL{{{_.authors_full}}}\n"
        "\\def \\authorsABBRV{{{_.authors_abbrv}}}\n"
        "\\def \\authorsSHORT{{{_.authors_short}}}\n"
        "\\title{{\\articleTITLE}}\n"
        "\\date{{}}\n"
        "".format(filename=filename, _=article, abstract=abstract)
    )

    for author in article.authors:
        affiliations = ",".join(author.affiliations)
        if len(author.orcid) > 0:
            affiliations += f",\\orcid{{{author.orcid}}}"
        content += f"\\author[{affiliations}]{{{author.name}}}\n"

    for affiliation in article.affiliations:
        if len(affiliation.address) > 0:
            content += "\\affil[{_.code}]{{{_.name}, {_.address}}}\n".format(
                _=affiliation
            )
        else:
            content += "\\affil[{_.code}]{{{_.name}}}\n".format(_=affiliation)

    return content


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import locale
    import argparse
    from article import Article

    # Set to a UTF-8 locale
    # Any non-ascii characters in the metadata in metadata.yaml
    # should be in UTF-8
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    parser = argparse.ArgumentParser(description="YAML to latex converter.")
    parser.add_argument(
        "--input",
        "-i",
        dest="filename_in",
        action="store",
        default="metadata.yaml",
        help="input YAML file",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="filename_out",
        action="store",
        default="article-metadata.tex",
        help="output latex file",
    )
    args = parser.parse_args()

    filename_in = args.filename_in
    filename_out = args.filename_out

    with open(filename_in, "r") as file:
        article = Article(file.read())

    if len(article.authors) > 0:
        content = generate_latex_metadata(filename_in, article)
        if filename_out is not None:
            with open(filename_out, "w") as file:
                file.write(content)
        else:
            print(content)
    else:
        print("Error! No author found.")

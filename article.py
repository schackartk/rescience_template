"""
ReScience yaml parser
Released under the BSD two-clauses licence
"""

from dataclasses import dataclass
from typing import Iterable

import yaml

SUFFIXES = ["II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


# -----------------------------------------------------------------------------
@dataclass
class Contributor:
    """Contributor to ReScience submission"""

    role: str
    name: str
    orcid: str = ""
    email: str = ""
    affiliations: Iterable = ()

    def __post_init__(self):
        self.fullname = self.name
        self.lastname = get_lastname(self.name)
        self.abbrvname = get_abbrvname(self.name)


# -----------------------------------------------------------------------------
@dataclass
class Affiliation:
    """Contributor affiliation"""

    code: str
    name: str
    address: str = ""


# -----------------------------------------------------------------------------
@dataclass
class Repository:
    """Code repository of submission"""

    name: str
    url: str
    doi: str
    swh: str = ""


# -----------------------------------------------------------------------------
@dataclass
class Replication:
    """Replication article"""

    cite: str
    bib: str
    url: str
    doi: str


# -----------------------------------------------------------------------------
@dataclass
class Review:
    """Information about reviewing"""

    url: str
    doi: str


# -----------------------------------------------------------------------------
class Date:
    """Date"""

    def __init__(self, date: str):
        try:
            import dateutil.parser

            date = dateutil.parser.parse(date)
            self.date = date
            self.year = date.year
            self.month = date.month
            self.day = date.day
            self.textual = self.date.strftime("%d %B %Y")
        except:
            import datetime

            now = datetime.datetime.now()
            self.date = now
            self.year = now.year
            self.month = now.month
            self.day = now.day
            self.textual = ""

    def __str__(self):
        return self.textual
        # return self.date.strftime("%d %B %Y")

    def __repr__(self):
        return self.textual
        # return self.date.strftime("%d %B %Y")


# -----------------------------------------------------------------------------
class Article:
    """Information about article"""

    def __init__(self, data):
        self.title = ""
        self.absract = ""
        self.type = ""
        self.domain = ""
        self.language = ""
        self.bibliography = ""
        self.keywords = []
        self.authors = []
        self.editors = []
        self.reviewers = []
        self.affiliations = []
        self.code = ""
        self.data = ""
        self.contact = ""

        self.review = ""
        self.replication = ""

        self.date_received = ""
        self.date_accepted = ""
        self.date_published = ""

        self.journal_name = ""
        self.journal_issn = ""
        self.journal_volume = ""
        self.journal_issue = ""
        self.article_number = ""
        self.article_doi = ""
        self.article_url = ""

        self.parse(data)

        # Build authors list
        self.authors_short = ""  # Family names only
        self.authors_abbrv = ""  # Abbreviated firsnames + Family names
        self.authors_full = ""  # Full names

        n_authors = len(self.authors)
        if n_authors > 3:
            self.authors_short = self.authors[0].lastname + " et al."
            self.authors_abbrv = self.authors[0].abbrvname + " et al."
            self.authors_full = self.authors[0].fullname + " et al."
        elif n_authors == 1:
            self.authors_short += self.authors[0].lastname
            self.authors_abbrv += self.authors[0].abbrvname
            self.authors_full += self.authors[0].fullname
        else:
            for author_i in range(n_authors - 2):
                self.authors_short += self.authors[author_i].lastname + ", "
                self.authors_abbrv += self.authors[author_i].abbrvname + ", "
                self.authors_full += self.authors[author_i].fullname + ", "

            if n_authors >= 2:
                self.authors_short += self.authors[n_authors - 2].lastname + " and "
                self.authors_short += self.authors[n_authors - 1].lastname

                self.authors_abbrv += self.authors[n_authors - 2].abbrvname + " and "
                self.authors_abbrv += self.authors[n_authors - 1].abbrvname

                self.authors_full += self.authors[n_authors - 2].fullname + " and "
                self.authors_full += self.authors[n_authors - 1].fullname

    def parse(self, data):
        """Parse YAML metadata file"""
        document = yaml.load(data, Loader=yaml.SafeLoader)

        self.title = document.get("title", "")
        self.abstract = document.get("abstract", "") or ""
        self.keywords = document["keywords"] or ""
        self.type = document["type"] or ""
        self.domain = document["domain"] or ""
        self.language = document["language"] or ""
        self.bibliography = document["bibliography"] or ""

        # Miscellaneous dates
        dates = {
            key: value for data in document["dates"] for key, value in data.items()
        }
        self.date_received = Date(dates["received"] or "")
        self.date_accepted = Date(dates["accepted"] or "")
        self.date_published = Date(dates["published"] or "")

        # Add authors
        for item in document["authors"]:
            role = "author"
            name = item["name"] or ""
            orcid = item.get("orcid", "") or ""
            email = item.get("email", "") or ""
            if item["affiliations"] is not None:
                if len(str(item["affiliations"])) > 1:
                    affiliations = item["affiliations"].split(",")
                    if "*" in affiliations:
                        affiliations.remove("*")
                        author = Contributor(role, name, orcid, email, affiliations)
                        self.add_contributor(author)
                        self.contact = author
                    else:
                        author = Contributor(role, name, orcid, email, affiliations)
                        self.add_contributor(author)
                else:
                    affiliations = list(str(item["affiliations"]))
                    author = Contributor(role, name, orcid, email, affiliations)
                    self.add_contributor(author)

        # Add author affiliations
        for item in document["affiliations"]:
            self.affiliations.append(
                Affiliation(item["code"], item["name"], item.get("address", ""))
            )

        # Add editor & reviewers
        for item in document["contributors"]:
            role = item["role"]
            name = item["name"] or ""
            orcid = item.get("orcid", "") or ""
            contributor = Contributor(role, name, orcid)
            self.add_contributor(contributor)

        # Code repository (mandatory)
        if "code" in document.keys():
            code = {
                key: value for data in document["code"] for key, value in data.items()
            }
            self.code = Repository(
                "code",
                code.get("url", "") or "",
                code.get("doi", "") or "",
                code.get("swh", "") or "",
            )
        else:
            raise IndexError("Code repository not found")

        # Data repository (optional)
        if "data" in document.keys():
            data = {
                key: value for data in document["data"] for key, value in data.items()
            }
            self.data = Repository(
                "data", data.get("url", "") or "", data.get("doi", "") or ""
            )
        else:
            self.data = Repository("data", "", "")

        # Review
        review = {
            key: value for review in document["review"] for key, value in review.items()
        }
        self.review = Review(review.get("url", "") or "", review.get("doi", "") or "")

        # Replication
        replication = {
            key: value
            for replication in document["replication"]
            for key, value in replication.items()
        }
        self.replication = Replication(
            replication["cite"] or "",
            replication["bib"] or "",
            replication["url"] or "",
            replication["doi"] or "",
        )

        # Article number & DOI
        article = {
            key: value
            for article in document["article"]
            for key, value in article.items()
        }
        self.article_number = article["number"] or ""
        self.article_doi = article["doi"] or ""
        self.article_url = article["url"] or ""

        # Journal volume and issue
        journal = {
            key: value
            for journal in document["journal"]
            for key, value in journal.items()
        }
        self.journal_name = str(journal.get("name", ""))
        self.journal_issn = str(journal.get("issn", ""))
        self.journal_volume = journal["volume"] or ""
        self.journal_issue = journal["issue"] or ""

    def add_contributor(self, contributor: Contributor):
        """Add contributor based on role"""
        if contributor.role == "author":
            self.authors.append(contributor)
        elif contributor.role == "editor":
            self.editors.append(contributor)
        elif contributor.role == "reviewer":
            self.reviewers.append(contributor)
        else:
            raise IndexError


# -----------------------------------------------------------------------------
def get_abbrvname(name: str) -> str:
    """
    Get contributor's abbreviated name

    Arguments:
    `name`: name as it appears in metadata.yaml
    """
    if not name:
        return ""

    if "," in name:
        lastname = name.split(",")[0]
        firstnames = name.split(",")[1].strip().split(" ")
    else:
        lastname = name.split(" ")[-1]
        firstnames = name.split(" ")[:-1]
        if lastname in SUFFIXES:
            lastname = " ".join(name.split(" ")[-2:])
            firstnames = name.split(" ")[:-2]
    abbrvname = ""
    for firstname in firstnames:
        if "-" in firstname:
            for name in firstname.split("-"):
                abbrvname += name[0].strip().upper() + ".-"
            abbrvname = abbrvname[:-1]
        else:
            abbrvname += firstname[0].strip().upper() + "."
    return abbrvname + " " + lastname


# -----------------------------------------------------------------------------
def test_get_lastname() -> None:
    """Test get_lastname()"""

    # No name
    assert get_lastname("") == ""

    # Last, First M.I.
    assert get_lastname("Rougier, Nicolas P.") == "Rougier"

    # First M.I. Last
    assert get_lastname("Nicolas P. Rougier") == "Rougier"

    # Last Suffix, First M.I.
    assert get_lastname("Schackart III, Kenneth E.") == "Schackart III"

    # First M.I. Last Suffix
    assert get_lastname("Kenneth E. Schackart III") == "Schackart III"


# -----------------------------------------------------------------------------
def get_lastname(name: str) -> str:
    """
    Get contributor's last name

    Arguments:
    `name`: name as it appears in metadata.yaml
    """
    if not name:
        return ""
    if "," in name:
        lastname = name.split(",")[0].strip()
    else:
        lastname = name.split(" ")[-1]
        if lastname in SUFFIXES:
            lastname = " ".join(name.split(" ")[-2:])
    return lastname


# -----------------------------------------------------------------------------
def test_get_abbrvname() -> None:
    """Test get_abbrvname()"""

    # No name
    assert get_abbrvname("") == ""

    # Last, First M.I.
    assert get_abbrvname("Rougier, Nicolas P.") == "N.P. Rougier"

    # First M.I. Last
    assert get_abbrvname("Nicolas P. Rougier") == "N.P. Rougier"

    # Last Suffix, First M.I.
    assert get_abbrvname("Schackart III, Kenneth E.") == "K.E. Schackart III"

    # First M.I. Last Suffix
    assert get_abbrvname("Kenneth E. Schackart III") == "K.E. Schackart III"


# -----------------------------------------------------------------------------
def main() -> None:
    """Main function"""
    with open("metadata.yaml") as file:
        article = Article(file.read())
        print(article.authors_full)
        print(article.authors_abbrv)
        print(article.authors_short)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()

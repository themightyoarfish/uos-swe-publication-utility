import pybtex.database
from pylatexenc.latex2text import LatexNodes2Text  # to unescape latex
from pathlib import Path
import re
import PyPDF2
from difflib import SequenceMatcher


def get_title_info(entry):
    """Try to guess title information from a publication."""
    if isinstance(entry, Path):
        pdf = PyPDF2.PdfFileReader(str(entry))
        if '/Title' in pdf.documentInfo:
            return pdf.documentInfo['/Title']
        else:
            return None
    elif type(entry) is pybtex.database.Entry:
        if 'title' in entry.fields:
            return LatexNodes2Text().latex_to_text(entry.fields['title'])
        elif 'booktitle' in entry.fields:
            return LatexNodes2Text().latex_to_text(entry.fields['booktitle'])
        else:
            return None
    else:
        raise NotImplementedError("Can only handle pdf or bib objects (was %s)"
                                  % type(entry))


def get_author_info(entry):
    """Try to extract some form of author string from a bibitem

    :entry: BibliographyData
    :returns: str -- String with author info or None, if nothing found

    """
    if isinstance(entry, Path):
        pdf = PyPDF2.PdfFileReader(str(entry))
        if '/Author' in pdf.documentInfo:
            return pdf.documentInfo['/Author']
        else:
            # last straw: filename
            return entry.stem
    elif type(entry) is pybtex.database.Entry:
        author1 = ''
        author2 = ''
        author3 = ''
        if 'author' in entry.fields:
            author1 = str(entry.fields['author'])
        if 'authors' in entry.fields:
            author2 = entry.fields['authors']
        if 'author' in str(entry.persons):
            persons = [' '.join(p.first_names + p.middle_names + p.last_names)
                       for p in entry.persons['author']]
            author3 = ' '.join(persons)
        if 'editor' in str(entry.persons):
            persons = [' '.join(p.first_names + p.middle_names + p.last_names)
                       for p in entry.persons['editor']]
            author3 = ' '.join(persons)

        author_info = LatexNodes2Text().latex_to_text(' '.join((author1,
                                                                author2,
                                                                author3)))
        if author_info:
            return author_info.strip()
        else:
            return None
    else:
        raise NotImplementedError("Can only handle pdf or bib objects (was %s)"
                                  % type(entry))


def pdf_for_pub(bibdata, pdf_folder):
    """Attempt to guess which pdf file might belong to a given bibliography entry.

    :bibdata: BibliographyData object
    :pdf_folder: str denoting folder location
    :returns: str

    """
    pdf_path = Path(pdf_folder)
    if not pdf_path.exists():
        raise OSError('Folder %s does not exist.' % pdf_folder)
    if not pdf_path.is_dir():
        raise OSError('%s is not a folder.' % pdf_folder)
    else:
        match = None
        confidence = 0
        for file in pdf_path.iterdir():
            author_info     = get_author_info(bibdata)
            title_info      = get_title_info(bibdata)
            author_info_pdf = get_author_info(file)
            confidence_title = search_for_string(file, title_info)
            confidence_author = SequenceMatcher(None, author_info_pdf.split(),
                                                author_info.split(),
                                                autojunk=False).ratio()
            new_confidence = (3 * confidence_title + confidence_author) / 4
            if confidence < new_confidence:
                confidence = new_confidence
                match = file
        if match and 'title' in bibdata.fields:
            print('Match for %s: %s, score=%d' % (bibdata.title, match,
                                                  confidence))
        return match


def search_for_string(pdf, text):
    """Scan a pdf file for a string and return best match + score.

    :pdf: PyPDF2.PdfFileReader -- file containing the pdf
    :text: str -- String to search for
    :returns: TODO

    """
    if not isinstance(pdf, PyPDF2.PdfFileReader):
        pdf = PyPDF2.PdfFileReader(str(pdf))
    if not isinstance(text, list):
        text = text.split()
    text_set = set(text)
    pdf_text = ' '.join([page.extractText() for page in pdf.pages])
    # remove newlines and superfluous spaces
    pdf_text = re.sub('[\n\s]+', ' ', pdf_text).split()
    # title should occur in first third (hopefully)
    pdf_text = pdf_text[:len(pdf_text)//3]
    best_score = 0
    best_match = None
    print("Searching for: %s" % text)
    for start in range(0, len(pdf_text)-len(text)):
        subsequence = pdf_text[start:start+len(text)]
        if text_set.intersection(set(subsequence)) == set():
            continue
        score = SequenceMatcher(None, subsequence, text, autojunk=False).ratio()
        if score > best_score:
            best_score = score
            best_match = subsequence
    if best_match:
        print("Best match for\n%s:\n%s\nscore=%d" % (text, best_match,
                                                     best_score))
    return best_score

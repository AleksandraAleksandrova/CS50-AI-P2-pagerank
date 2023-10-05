import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = dict()
    all_pages = len(corpus.keys())
    
    if page in corpus.keys():
        linked_pages = len(corpus[page])
    else:
        linked_pages = 0
    
    for current_page in corpus.keys():
        probability_distribution[current_page] = (1-damping_factor)/all_pages

    if linked_pages != 0:
        for current_page in corpus[page]:
            probability_distribution[current_page] += damping_factor/linked_pages
    
    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    for page in corpus.keys():
        pagerank[page] = 0
    
    current_sample = random.choice(list(corpus.keys()))
    for i in range(n-1):
        current_distribution = transition_model(corpus, current_sample, damping_factor)
        for page in pagerank.keys():
            pagerank[page] += current_distribution[page] / n
        current_sample = random.choices(list(current_distribution.keys()), list(current_distribution.values()))[0]

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    N = len(corpus.keys())
    for page in corpus.keys():
        pagerank[page] = 1/N

    while True:
        new_pagerank = dict()
        converged = True 
        for page in corpus.keys():
            new_pagerank[page] = (1-damping_factor)/N
            for i in corpus.keys():
                if page in corpus[i]:
                    new_pagerank[page] += damping_factor * pagerank[i] / len(corpus[i])
        
        for page in corpus.keys():
            if abs(new_pagerank[page] - pagerank[page]) >= 0.001:
                converged = False
                break 

        if converged:
            break
    
        pagerank = new_pagerank

    return pagerank


if __name__ == "__main__":
    main()

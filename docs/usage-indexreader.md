# Pyserini: Usage of the Index Reader API

The `IndexReader` class provides methods for accessing and manipulating an inverted index.

**IMPORTANT NOTE:** Be aware whether a method takes or returns _analyzed_ or _unanalyzed_ terms.
"Analysis" refers to processing by a Lucene `Analyzer`, which typically includes tokenization, stemming, stopword removal, etc.
For example, if a method expects the unanalyzed term and is called with an analyzed term, it'll reanalyze the term; it is sometimes the case that analysis of an already analyzed term is also a valid term, which means that the method will return incorrect results without triggering any warning or error.

Initialize the class as follows:

```python
from pyserini import analysis, index

index_reader = index.IndexReader('indexes/index-robust04-20191213/')
```

Use `terms()` to grab an iterator over all terms in the collection, i.e., the dictionary.
Note that these terms are _analyzed_.
Here, we only print out the first 10:

```python
import itertools
for term in itertools.islice(index_reader.terms(), 10):
    print(f'{term.term} (df={term.df}, cf={term.cf})')
```

How to fetch term statistics for a particular (unanalyzed) query term, "cities" in this case:

```python
term = 'cities'

# Look up its document frequency (df) and collection frequency (cf).
# Note, we use the unanalyzed form:
df, cf = index_reader.get_term_counts(term)
print(f'term "{term}": df={df}, cf={cf}')
```

What if we want to fetch term statistics for an analyzed term?
This can be accomplished by setting `Analyzer` to `None`:

```python
term = 'cities'

# Analyze the term.
analyzed = index_reader.analyze(term)
print(f'The analyzed form of "{term}" is "{analyzed[0]}"')

# Skip term analysis:
df, cf = index_reader.get_term_counts(analyzed[0], analyzer=None)
print(f'term "{term}": df={df}, cf={cf}')
```

Here's how to fetch and traverse postings:

```python
# Fetch and traverse postings for an unanalyzed term:
postings_list = index_reader.get_postings_list(term)
for posting in postings_list:
    print(f'docid={posting.docid}, tf={posting.tf}, pos={posting.positions}')

# Fetch and traverse postings for an analyzed term:
postings_list = index_reader.get_postings_list(analyzed[0], analyzer=None)
for posting in postings_list:
    print(f'docid={posting.docid}, tf={posting.tf}, pos={posting.positions}')
```

Here's how to fetch the document vector for a document:

```python
doc_vector = index_reader.get_document_vector('FBIS4-67701')
print(doc_vector)
```

The result is a dictionary where the keys are the analyzed terms and the values are the term frequencies.
To compute the tf-idf representation of a document, do something like this:

```python
tf = index_reader.get_document_vector('FBIS4-67701')
df = {term: (index_reader.get_term_counts(term, analyzer=None))[0] for term in tf.keys()}
```

The two dictionaries will hold tf and df statistics; from those it is easy to assemble into the tf-idf representation.
However, often the BM25 score is better than tf-idf.
To compute the BM25 score for a particular term in a document:

```python
# Note that the keys of get_document_vector() are already analyzed, we set analyzer to be None.
bm25_score = index_reader.compute_bm25_term_weight('FBIS4-67701', 'citi', analyzer=None)
print(bm25_score)

# Alternatively, we pass in the unanalyzed term:
bm25_score = index_reader.compute_bm25_term_weight('FBIS4-67701', 'city')
print(bm25_score)
```

And so, to compute the BM25 vector of a document:

```python
tf = index_reader.get_document_vector('FBIS4-67701')
bm25_vector = {term: index_reader.compute_bm25_term_weight('FBIS4-67701', term, analyzer=None) for term in tf.keys()}
```

Another useful feature is to compute the score of a _specific_ document with respect to a query, with the `compute_query_document_score` method.
For example:

```python
query = 'hubble space telescope'
docids = ['LA071090-0047', 'FT934-5418', 'FT921-7107', 'LA052890-0021', 'LA070990-0052']

for i in range(0, len(docids)):
    score = index_reader.compute_query_document_score(docids[i], query)
    print(f'{i+1:2} {docids[i]:15} {score:.5f}')
```

The scores should be very close (rounding at the 4th decimal point) to the results above, but not _exactly_ the same because `search` performs additional score manipulation to break ties during ranking.

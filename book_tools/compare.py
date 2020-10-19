import re
import numpy as np
import pandas as pd
from ftfy import fix_text
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as ct
from recordlinkage.base import BaseCompareFeature
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def ngrams(string, n=3):
    string = fix_text(string) # fix text encoding issues
    string = string.encode("ascii", errors="ignore").decode() #remove non ascii chars
    string = string.lower() #make lower case
    chars_to_remove = [")","(",".","|","[","]","{","}","'"]
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
    string = re.sub(rx, '', string) #remove the list of chars defined above
    string = string.replace('&', 'and')
    string = string.replace(',', ' ')
    string = string.replace('-', ' ')
    string = string.title() # normalise case - capital at start of each word
    string = re.sub(' +',' ',string).strip() # get rid of multiple spaces and replace with a single space
    string = ' '+ string +' ' # pad names for ngrams...
    string = re.sub(r'[,-./]|\sBD',r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def awesome_cossim_top(A, B, ntop, lower_bound=0):
    """ Faster cossine similarity. Returns only top matches.
    """
    # force A and B as a CSR matrix.
    # If they have already been CSR, there is no overhead
    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape

    idx_dtype = np.int32

    nnz_max = M*ntop

    indptr = np.zeros(M+1, dtype=idx_dtype)
    indices = np.zeros(nnz_max, dtype=idx_dtype)
    data = np.zeros(nnz_max, dtype=A.dtype)

    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, indices, data
    )
    return csr_matrix((data,indices,indptr),shape=(M,N))


def get_matches_df(sparse_matrix, name_vector, top=None):
    non_zeros = sparse_matrix.nonzero()

    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similarity = np.zeros(nr_matches)

    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similarity[index] = sparse_matrix.data[index]

    # Create DataFrame with MultiIndex
    df = pd.DataFrame(
        {
            'left': left_side,
            'right': right_side,
            'similarity': similarity
        }
    )
    return df


class TFIDF(BaseCompareFeature):

    def _compute(self, data1, data2):
        corpus = pd.concat([data1[0], data2[0]]).unique()
        # Break strings into ngrams and convert to a matrix of TF-IDF features.
        vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
        tf_idf_matrix = vectorizer.fit_transform(corpus)
        # Calculate similarities
        similarity_matrix = pd.DataFrame(
            cosine_similarity(tf_idf_matrix, tf_idf_matrix)
        )
        similarity_matrix.columns = corpus
        similarity_matrix['index'] = pd.Series(corpus)
        similarity_matrix.set_index('index', inplace=True)
        pairs = zip(data1[0], data2[0])
        return pd.Series(
            [similarity_matrix.loc[r, c] for r, c in pairs]
        )

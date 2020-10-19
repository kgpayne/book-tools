import fuzzy
import pandas as pd
from itertools import product
from recordlinkage.utils import listify
from recordlinkage.base import BaseIndexAlgorithm


class Soundex(BaseIndexAlgorithm):

    def __init__(self, left_on, right_on=None, **kwargs):
        super().__init__(**kwargs)
        self.left_on = listify(left_on)
        self.right_on = listify(right_on) if right_on else self.left_on
        self.soundex = fuzzy.Soundex(4)

    def  _link_index(self, df_a, df_b):

        soundex_left = df_a[self.left_on].applymap(self.soundex)
        soundex_right = df_b[self.right_on].applymap(self.soundex)

        candidate_pairs = []
        for left_key, left_grp in soundex_left.groupby(by=self.left_on):
            for right_key, right_grp in soundex_right.groupby(by=self.right_on):
                if left_key == right_key:
                    candidate_pairs.extend(
                        product(left_grp.index.values, right_grp.index.values)
                    )

        # Make a product of the two numpy arrays
        return pd.MultiIndex.from_tuples(
            candidate_pairs,
            names=[df_a.index.name, df_b.index.name]
        )

import re
import numpy as np
import pandas as pd
from ftfy import fix_text
from nameparser import HumanName


def to_snake_case(str):
    res = [str[0].lower()]
    for c in str[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            res.append('_')
            res.append(c.lower())
        else:
            res.append(c)

    return ''.join(res)


class Cleaner:

    def __init__(self, steps=[]):
        self.steps = []
        self.add(steps)

    def add(self, step):
        """Add a clean step.

        This method is used to add clean steps.

        Parameters
        ----------
        step : list, class
            A (list of) clean step(s) from
            :mod:`book_tools.cleaner`.
        """
        if isinstance(step, list):
            self.steps.extend(step)
        else:
            self.steps.append(step)

    def compute(self, df, clear=True):
        """ Execute clean steps.
        """
        for step in self.steps:
            df = step.compute(df)
        if clear:
            self.steps = []
        return df


class BaseCleanStep:

    def __init__(
        self, label, *args, out_label=None, keep_original=False, **kwargs
    ):
        self.label = label
        self.args = args
        self.kwargs = kwargs
        self.out_label = out_label
        self.keep_original = keep_original

    def _compute(self, df, assign_to, apply_to):
        df.loc[:, assign_to] = df[apply_to].apply(
            lambda x: self._f_clean_func(x, *self.args, **self.kwargs)
        )
        return df

    def compute(self, df):
        if self.out_label:
            df = self._compute(df, assign_to=self.out_label, apply_to=self.label)
        else:
            if self.keep_original:
                new_label = f"o__{to_snake_case(self.label)}"
                if not new_label in df.columns:
                    df[new_label] = df[self.label]
            df = self._compute(df, assign_to=self.label, apply_to=self.label)
        return df.copy(deep=True)


class FillNA(BaseCleanStep):

    def _compute(self, df, assign_to, apply_to):
        df.loc[:, assign_to] = df[apply_to].fillna(*self.args, **self.kwargs)
        return df


class Exclude(BaseCleanStep):

    def compute(self, df):
        exclusions = self.kwargs.pop('exclusions')
        exc = df.loc[df[self.label].isin(exclusions)]
        return df.loc[~df.index.isin(exc.index)]


class Substitute(BaseCleanStep):

    def _f_clean_func(self, string, subs):
        if string in subs:
            return subs[string]
        else:
            return string


class FTFYFixText(BaseCleanStep):

    def _f_clean_func(self, string):
        return fix_text(string)


class RemoveNonAscii(BaseCleanStep):

    def _f_clean_func(self, string):
        return string.encode("ascii", errors="ignore").decode() #remove non ascii chars


class FixMultipleSpaces(BaseCleanStep):

    def _f_clean_func(self, string):
        return re.sub(' +', ' ', string).strip() # get rid of multiple spaces and replace with a single space


class PadPunctuation(BaseCleanStep):

    def _f_clean_func(self, string):
        return (
            re.sub(r'(?<=[.,])(?=[^\s])', r' ', string)  # Add spaces after punctuation e.g. 'J.K. Rowling' > 'J. K. Rowling'
            .lstrip().rstrip()
        )


class ParseHumanName(BaseCleanStep):

    def _f_clean_func(self, string):
        human = HumanName(string)
        return human.first, human.middle, human.last


class Lower(BaseCleanStep):

    def _f_clean_func(self, string):
        return string.lower()


class RemovePunctuation(BaseCleanStep):

    def _f_clean_func(self, string):
        return re.sub('[^A-Za-z0-9 ]+', '', string)


class FixedListLength(BaseCleanStep):
    """ Given a list-like column value, pad or truncate the list to a fixed-width.
    """

    def _f_clean_func(self, lst, length, pad_value=None):
        new_list = []
        for itm in lst:
            if len(new_list) < length:
                new_list.append(itm)
            else:
                break
        if len(new_list) < length:
            # pad list
            while len(new_list) < length:
                new_list.append(pad_value)
        return new_list


class Split(BaseCleanStep):

    def _f_clean_func(self, string, separator, maxsplit):
        return string.split(separator, maxsplit)


class ListFlatten(BaseCleanStep):

    def _f_clean_func(self, lst):
        return [item for sublist in lst for item in sublist]


class SplitCombinedNames(BaseCleanStep):
    """ Recursively split multiple authors joined by '&| and |,'
    """

    def split_combined_names(self, names):
        expanded_names = []

        if not isinstance(names, list):
            names = [names]

        for name in names:
            if name:
                if ' and ' in name:
                    split_list = name.split(' and ')
                    expanded_names.extend(
                        self.split_combined_names(split_list)
                    )
                elif ' and' in name:
                    split_list = name.split(' and')
                    expanded_names.extend(
                        self.split_combined_names(split_list)
                    )
                elif ' & ' in name:
                    split_list = name.split(' & ')
                    expanded_names.extend(
                        self.split_combined_names(split_list)
                    )
                elif ',' in name:
                    split_list = name.split(',')
                    expanded_names.extend(
                        self.split_combined_names(split_list)
                    )
                else:
                    name = name.lstrip().rstrip()
                    if name:
                        expanded_names.append(name)
        return expanded_names

    def _f_clean_func(self, string):
        return self.split_combined_names(string)

#!/usr/bin/env python
# complement_finder.py
# Author: Julie Kallini


from conllu import parse_incr
import pandas as pd
from tqdm import tqdm
import argparse
from upos import upos


def get_args():
    '''
    Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Preprocess raw CoNLL-U file(s).')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input CoNLL-U file(s)')
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Main function.
    '''

    args = get_args()

    i = 1
    tot = str(len(args.input_files))

    WEAK_VERBS = ['make']

    # Iterate over input files
    for file_name in tqdm(args.input_files):

        file = open(file_name, "r", encoding="utf-8")
        data = []

        # Get tokenlist for each sentence in file
        for tokenlist in parse_incr(file):

            for tok in tokenlist:

                # Check if current token is direct object of a weak verb
                if tok['deprel'] == 'obj' and \
                        tokenlist[tok['head']-1]['lemma'] in WEAK_VERBS:

                    # Append information about the complement to dataset
                    row = []
                    row.append(tokenlist[tok['head']-1]['lemma'])
                    row.append(tok['upos'])
                    row.append(tok['lemma'])
                    row.append(tokenlist.metadata['text'])
                    data.append(row)

        # DataFrame
        columns = ['Verb', 'Complement Category',
                   'Complement Lemma', 'Sentence Text']

        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)

        # Ensure that only closed class categories are included
        valid_categories = [upos.NOUN, upos.VERB, upos.ADJ, upos.ADV]
        df = df[df['Complement Category'].isin(valid_categories)]

        # Write DataFrame to file
        dest_name = file_name.split('.')[0]
        df.drop_duplicates(inplace=True)
        df.to_csv(dest_name + '_comp.csv', index=False)

        i += 1

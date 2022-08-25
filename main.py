# given a feature matrix,
# create a list logically possible natural classes,
# and then get similarity of two segments. similarity_(p1,p2) = (# of shared) / ( #shared + #not_shared)
# and then create and export a similarity matrix

# define natural classes as a combination of valued features and one or more segments have that feature specification.

from itertools import product
import pandas as pd
import json
import os


def load_features(path):
    """
    loads a PCT feature matrix and return Segments each with feature info
    :param      path: str. path to a csv file
    :return     inventory: dict. key=segment name and value=list of feature values
                features: list. list of features
    """
    df = pd.read_csv(path)
    inventory = dict()
    for col in df:
        if 'Unnamed' in col:
            feature_names = [i.strip() for i in list(df[col].values)]
            continue

        feature_values = [i.strip() for i in list(df[col].values)]
        inventory[col.strip()] = feature_values

    return inventory, feature_names


def main(language_name, feature_matrix, method="frisch"):
    """
    Given a PCT-like segment-feature matrix, calculate similarity between a pair of two consonants.
    :param language_name: str. any name of a language
    :param feature_matrix: str. path to a PCT-like feature file in the csv format
    :param method: str. definition of segment similarity. default to Frisch et al 2004
    :return: list of possible natural classes
    """
    inventory, features = load_features(feature_matrix)

    if method == "frisch":
        if not os.path.exists(f"./output/{language_name}.json"):
            logical = possible_feature_combi(features=features)
            results_with_duplicates = NC_detect(inventory, logical)

            # remove duplicate values in results_with_duplicates
            temp = []
            nat_classes = dict()
            for key, val in results_with_duplicates.items():
                if val not in temp:
                    temp.append(val)
                    nat_classes[key] = val

            if not os.path.exists('output'):
                os.makedirs('output')
            with open(f"./output/{language_name}.json", "w+", encoding='utf-8') as write_file:
                json.dump(nat_classes, write_file, indent=4, ensure_ascii=False)
            print(f"[INFO] {language_name}.json created.")

        else:
            with open(f"./output/{language_name}.json", "r", encoding='utf-8') as json_file:
                nat_classes = json.load(json_file)
                type(nat_classes)
        segments = list(inventory.keys())

        # create similarity matrix as df
        sim_mat = pd.DataFrame(columns=segments)

        # populate sim_mat (row by row)
        for s in segments:
            similarities = [sim(s, c2, nat_classes) for c2 in segments]
            sim_mat.loc[s] = similarities

        sim_mat.to_csv(f'./output/{language_name}_similarity_matrix.csv')
        print(f"\n[INFO] similarity matrix for {language_name} created.")
        print(f"[INFO] find {language_name}_similarity_matrix.csv in the ./output folder.")


def sim(c1, c2, nc):
    """
    get two consonant segments and return their similarity value
    :param c1: str. consonant segment
    :param c2: str. consonant segment
    :param nc: dict. dictionary of natural classes in which c1 and c2 should be compared
    :return similarity: int. similarity value
    """

    ## similarity = (num of shared NC between C1 and C2) / { ( number of shared NC ) + ( number of not shared NC ) }
    list_nc = list(nc.values())
    c1_classes = set()  # set of natural classes with c1 in them
    c2_classes = set()  # set of natural classes with c1 in them

    for n in list_nc:
        if c1 in n:
            c1_classes.add(', '.join(n))
        if c2 in n:
            c2_classes.add(', '.join(n))

    shared = len(c1_classes.intersection(c2_classes))  # number of shared natural classes between the two segments
    not_shared = len(c1_classes.symmetric_difference(c2_classes))  # number of natural classes to which only one segment belongs

    similarity = shared / (shared + not_shared)

    return similarity


def NC_detect(inventory, logical):
    res = dict()
    total_length = 3 ** 10
    ind = 0
    for ind, l in enumerate(logical):
        l = list(l)
        print(f"[INFO] running feature combination {ind} / {total_length}")
        print(f"[INFO] found NC {len(res)}")
        uns_indices = [i for i, x in enumerate(l) if x == 0]
        if len(uns_indices) < 1:
            var = [i for i, x in enumerate(list(inventory.values())) if x == l]
            if len(var) > 0:
                res[str(l)] = var
        else:
            res[str(l)] = []
            segments = list(inventory.keys())
            prev_u = 0
            for u in uns_indices:
                checking = l[prev_u:u]
                to_delete = []
                for ind, seg in enumerate(segments):
                    if inventory[seg][prev_u:u] != checking:
                        to_delete.append(ind)

                for delete in reversed(to_delete):
                    del segments[delete]

                prev_u = u+1
            if u < len(l)-1:
                checking = l[u+1:len(l)]
                to_delete = []
                for ind, seg in enumerate(segments):
                    if inventory[seg][u+1:len(l)] != checking:
                        to_delete.append(ind)
                for delete in reversed(to_delete):
                    del segments[delete]
            res[str(l)] = segments
            if len(res[str(l)]) == 0:
                del res[str(l)]
    return res


def possible_feature_combi(features):
    """
    list of logically possible feature combinations. incl. all none specification
    :param features: list of features
    :return: list of possible feature combinations
    """
    valuation = ['+', '-', 0]
    return product(valuation, repeat=len(features))


if __name__ == '__main__':
    lang = 'maltese'
    path = "./features.csv"
    main(lang, path)

import json
import os

import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer

prefix_metaprogram = "metaprogram_db"
metaprogram_dict = {}
for metaprogram_file in os.listdir(prefix_metaprogram):
    print(metaprogram_file)
    metaprogram_df = pd.read_csv(prefix_metaprogram + "/" + metaprogram_file)
    temp_metaprograms = pd.DataFrame()
    temp_metaprograms = temp_metaprograms.append(metaprogram_df, sort=True)
    temp_metaprograms = temp_metaprograms.fillna(0)
    ref_metaprograms = temp_metaprograms.groupby(by="sentence").sum().reset_index()
    ref_metaprograms.index.set_names(['sentence'])
    # print(ref_metaprograms.info())
    metaprograms = list(ref_metaprograms.drop("sentence", axis=1).keys())
    corpus = ref_metaprograms["sentence"].dropna()
    vectorizer = CountVectorizer()
    # print(corpus)
    transf_corpus = vectorizer.fit_transform(corpus.values)
    # print(transf_corpus.toarray())
    # print(vectorizer.get_feature_names())
    metaprogram_dict[metaprogram_df.keys()[0]] = (vectorizer,
                                                  NearestNeighbors(n_neighbors=1, algorithm='brute').fit(
                                                      transf_corpus),
                                                  ref_metaprograms)

print(len(metaprogram_dict))
meta_programs = metaprogram_dict.keys()

prefix_logiclevel = "logiclevel_db"
logiclevel_dict = {}
for logiclevel_file in os.listdir(prefix_logiclevel):
    print(logiclevel_file)
    logiclevel_df = pd.read_csv(prefix_logiclevel + "/" + logiclevel_file)
    temp_logiclevels = pd.DataFrame()
    temp_logiclevels = temp_logiclevels.append(logiclevel_df, sort=True)
    temp_logiclevels = temp_logiclevels.fillna(0)
    ref_logiclevels = temp_logiclevels.groupby(by="sentence").sum().reset_index()
    ref_logiclevels.index.set_names(['sentence'])
    print(ref_logiclevels.info())
    logiclevels = list(ref_logiclevels.drop("sentence", axis=1).keys())
    corpus = ref_logiclevels["sentence"].dropna()
    vectorizer = CountVectorizer()
    print(corpus)
    transf_corpus = vectorizer.fit_transform(corpus.values)
    # print(transf_corpus.toarray())
    # print(vectorizer.get_feature_names())
    logiclevel_dict[logiclevel_df.keys()[0]] = (vectorizer,
                                                NearestNeighbors(n_neighbors=1, algorithm='brute').fit(transf_corpus),
                                                ref_logiclevels)


class Modeler:

    def __init__(self, target):
        self.target = target
        self.profile = {program: 0 for program in meta_programs}
        self.models = metaprogram_dict
        self.ref_profile = self.profile
        self.ref_sentence = None

    def compute_profile(self, msg):
        profile = {program: 0 for program in meta_programs}
        for metaprogram, mp_model in self.models.items():
            print(metaprogram)
            vectorizer = mp_model[0]
            model = mp_model[1]
            ref_metaprogram = mp_model[2]
            transf_msg = vectorizer.transform([msg]).toarray()
            if not transf_msg[0].any():
                pass
            else:
                distances, indices = model.kneighbors(transf_msg)
                ref_indice = indices[0][0]
                mp_profile = ref_metaprogram.iloc[ref_indice].drop("sentence")
                mp_profile = mp_profile.to_dict()
                mp_name = list(mp_profile.keys())[0]
                mp_value = list(mp_profile.values())[0]
                profile[mp_name] = mp_value
                # self.ref_profile[mp_name] += mp_value
            # print(profile)
        print(profile)
        return profile

    def update_profile(self, msg):
        profile = self.compute_profile(msg)
        for key in self.profile:
            self.profile[key] += int(profile[key])
        return self

    def save_profile(self, path):
        with open(path, "w") as out_file:
            json.dump(self.profile, out_file)
        return self

    def load_profile(self, path):
        with open(path, "r") as in_file:
            self.profile = json.load(in_file)
        return self

    def create_profile_from_ref(self, ref_path):
        return self

    def check_inversion(self, sentence_profile):
        found_inversion = False
        inversion_keys = []
        for key in self.ref_sentence.keys():
            if sentence_profile[key] * self.ref_sentence[key] < 0:
                found_inversion = True
                inversion_keys.append(key)
            else:
                continue
        return found_inversion, inversion_keys


if __name__ == '__main__':
    import pytest

    pytest.main()

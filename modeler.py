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
metaprograms = metaprogram_dict.keys()

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
    # print(ref_logiclevels.info())
    logiclevels = list(ref_logiclevels.drop("sentence", axis=1).keys())
    corpus = ref_logiclevels["sentence"].dropna()
    vectorizer = CountVectorizer()
    # print(corpus)
    transf_corpus = vectorizer.fit_transform(corpus.values)
    # print(transf_corpus.toarray())
    # print(vectorizer.get_feature_names())
    logiclevel_dict[logiclevel_df.keys()[0]] = (vectorizer,
                                                NearestNeighbors(n_neighbors=1, algorithm='brute').fit(transf_corpus),
                                                ref_logiclevels)

print(len(logiclevel_dict))
logiclevelsprograms = logiclevel_dict.keys()


def find_neighbors(msg, model_dict):
    model_vectorizer = model_dict[0]
    model = model_dict[1]
    ref_metaprogram = model_dict[2]
    transf_msg = model_vectorizer.transform([msg]).toarray()
    if not transf_msg[0].any():
        return 0
    else:
        distances, indices = model.kneighbors(transf_msg)
        ref_indice = indices[0][0]
        profile = ref_metaprogram.iloc[ref_indice].drop("sentence")
        profile = profile.to_dict()
        value = list(profile.values())[0]
        return value


class Modeler:

    def __init__(self, target):
        self.target = target
        self.metaprogram_profile = {program: 0 for program in metaprograms}
        self.metaprogram_models = metaprogram_dict
        self.logiclevel_profile = {level: 0 for level in logiclevels}
        self.logiclevel_models = logiclevel_dict
        self.ref_profile = self.metaprogram_profile
        self.ref_sentence = None

    def compute_profile(self, msg):
        metaprogram_profile = {program: 0 for program in metaprograms}
        for metaprogram, mp_model in self.metaprogram_models.items():
            print(metaprogram)
            mp_value = find_neighbors(msg, mp_model)
            metaprogram_profile[metaprogram] = mp_value
            # print(profile)
        print(metaprogram_profile)

        logiclevel_profile = {level: 0 for level in logiclevels}
        for logiclevel, ll_model in self.logiclevel_models.items():
            #print(logiclevel)
            ll_value = find_neighbors(msg, ll_model)
            logiclevel_profile[logiclevel] = ll_value
            # print(profile)
        print(logiclevel_profile)

        return metaprogram_profile, logiclevel_profile

    def update_profile(self, msg):
        sentence_metaprograms_profile, sentence_logiclevels_profile = self.compute_profile(msg)
        #print(self.metaprogram_profile)
        #print(sentence_metaprograms_profile)
        for key in self.metaprogram_profile:
            self.metaprogram_profile[key] += int(sentence_metaprograms_profile[key])
        #print(self.logiclevel_profile)
        #print(sentence_logiclevels_profile)
        for key in self.logiclevel_profile:
            self.logiclevel_profile[key] += int(sentence_logiclevels_profile[key])
        return self

    def save_profile(self, path):
        with open(path, "w") as out_file:
            json.dump(self.metaprogram_profile, out_file)
        return self

    def load_profile(self, path):
        with open(path, "r") as in_file:
            self.metaprogram_profile = json.load(in_file)
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

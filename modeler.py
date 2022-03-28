import json
import os

import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer

temp_metaprograms = pd.DataFrame()
prefix = "knowledge_mp"
for meta_program_file in os.listdir(prefix):
    # print(meta_program_file)
    meta_program_df = pd.read_csv(prefix+"/"+meta_program_file)
    temp_metaprograms = temp_metaprograms.append(meta_program_df, sort=True)
temp_metaprograms = temp_metaprograms.fillna(0)
ref_metaprograms = temp_metaprograms.groupby(by="sentence").sum().reset_index()
ref_metaprograms.index.set_names(['sentence'])
# print(ref_metaprograms.info())
meta_programs = list(ref_metaprograms.drop("sentence", axis=1).keys())
corpus = ref_metaprograms["sentence"].dropna()
vectorizer = CountVectorizer()
#print(corpus)
transf_corpus = vectorizer.fit_transform(corpus.values)
# print(transf_corpus.toarray())
# print(vectorizer.get_feature_names())


class Modeler:

    def __init__(self, target):
        self.target = target
        self.profile = {program: 0 for program in meta_programs}
        self.model = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(transf_corpus)
        self.ref_profile = self.profile

    def compute_profile(self, msg):
        transf_msg = vectorizer.transform([msg]).toarray()
        if not transf_msg[0].any():
            profile = {program: 0 for program in self.profile.keys()}
        else:
            distances, indices = self.model.kneighbors(transf_msg)
            ref_indice = indices[0][0]
            profile = ref_metaprograms.iloc[ref_indice].drop("sentence")
            profile = profile.to_dict()
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
        for key in self.ref_profile.keys():
            if sentence_profile[key] * self.profile[key] < 0 :
                found_inversion = True
                inversion_keys.append(key)
            else:
                continue
        return found_inversion, inversion_keys


if __name__ == '__main__':
    import pytest
    pytest.main()

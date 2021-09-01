import json
import os

import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer

temp_metaprograms = pd.DataFrame()
prefix = "knowledge_mp"
for meta_program_file in os.listdir(prefix):
    print(meta_program_file)
    meta_program_df = pd.read_csv(prefix+"/"+meta_program_file)
    temp_metaprograms = temp_metaprograms.append(meta_program_df, sort=True)
temp_metaprograms = temp_metaprograms.fillna(0)
ref_metaprograms = temp_metaprograms.groupby(by="sentence").sum().reset_index()
ref_metaprograms.index.set_names(['sentence'])
print(ref_metaprograms.info())
meta_programs = list(ref_metaprograms.drop("sentence", axis=1).keys())
corpus = ref_metaprograms["sentence"].dropna()
vectorizer = CountVectorizer()
#print(corpus)
transf_corpus = vectorizer.fit_transform(corpus.values)
print(transf_corpus.toarray())
print(vectorizer.get_feature_names())


class Modeler:

    def __init__(self, target):
        self.target = target
        self.profile = {program: 0 for program in meta_programs}
        self.model = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(transf_corpus)

    def __compute_profile(self, msg):
        print("computing profile")
        print(msg)
        transf_msg = vectorizer.transform([msg]).toarray()
        print(transf_msg, sum(transf_msg[0]))
        print(transf_msg[0], transf_msg[0].any())
        if not transf_msg[0].any():
            profile = {program: 0 for program in self.profile.keys()}
        else:
            distances, indices = self.model.kneighbors(transf_msg)
            ref_indice = indices[0][0]
            print(ref_metaprograms.iloc[ref_indice])
            profile = ref_metaprograms.iloc[ref_indice].drop("sentence")
        for key in self.profile:
            self.profile[key] += int(profile[key])
        print(self.profile)
        return self

    def update_profile(self, msg_list):
        for msg in msg_list.split('.'):
            self.__compute_profile(msg)
        return self

    def save_profile(self, path):
        with open(path, "w") as out_file:
            print(self.profile)
            json.dump(self.profile, out_file)
        return self

    def load_profile(self, path):
        with open(path, "r") as in_file:
            self.profile = json.load(in_file)
        return self

    def create_profile_from_ref(self, ref_path):
        return self


if __name__ == '__main__':
    import pytest
    pytest.main()

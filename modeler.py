import json
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer

ref_metaprograms = pd.read_csv("meta_program_ref.csv")
meta_programs = list(ref_metaprograms.keys()[:-1])
corpus = ref_metaprograms["sentence"]
vectorizer = CountVectorizer()
transf_corpus = vectorizer.fit_transform(corpus)
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
        transf_msg = vectorizer.transform([msg["message"]]).toarray()
        print(transf_msg, sum(transf_msg[0]))
        print(transf_msg[0], transf_msg[0].any())
        if not transf_msg[0].any():
            profile = {program: 0 for program in self.profile.keys()}
        else:
            distances, indices = self.model.kneighbors(transf_msg)
            ref_indice = indices[0][0]
            profile = ref_metaprograms.iloc[ref_indice].drop("sentence")
        for key in self.profile:
            self.profile[key] += profile[key]
        print(self.profile)
        return self

    def update_profile(self, msg_list):
        for msg in msg_list.to_dict(orient="records"):
            self.__compute_profile(msg)
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


if __name__ == '__main__':
    import pytest
    pytest.main()
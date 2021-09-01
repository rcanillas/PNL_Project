import pandas as pd
import random
from sklearn.neighbors import NearestNeighbors
import math

answer_list = pd.read_csv("templates/meta_answers.csv")
answ_corpus = answer_list.drop(["text"], axis=1)
nn_model = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(answ_corpus)


class ResponseStrategy:
    def __init__(self, strategy="random"):
        self.strategy = strategy
        self.previously_selected = []

    def select_answer(self, answer_list, target_profile, nb_answers=0):
        answer = ""
        if self.strategy == "random":
            answer = random.choice(answer_list["text"].values)
        if self.strategy == "nearest_neighbors":
            print(target_profile)
            distances, indices = nn_model.kneighbors([list(target_profile.values())])
            ref_answer = indices[0][0]
            print(ref_answer, indices)
            answer = answer_list.iloc[ref_answer]['text']
        if self.strategy == "depth_analysis":
            answer_list = pd.read_csv("templates/depth_answers.csv")
            print("depth_analysis")
            depth_meter = math.floor((nb_answers-1)/3)
            print(nb_answers, depth_meter)
            if depth_meter <= max(answer_list["depth"]):
                answers = answer_list.loc[answer_list["depth"]==depth_meter]["text"]
                print(answers)
                answer = random.choice(answers.values)
                if len(answers) > len(self.previously_selected):
                    if answer in self.previously_selected:
                        answer = random.choice(answers.values)
            else:
                answer = "Je pense que nous avons fait le tour de la question ! Voici votre profil\n" +f"{target_profile}"
        return answer


class Answerer:
    def __init__(self, session):
        self.session = session
        self.conversation_data = pd.DataFrame()
        self.response_strategy = ResponseStrategy(strategy="depth_analysis")
        self.answer_list = pd.DataFrame()
        self.target_profile = None
        self.nb_answers = 0

    def load_conversation_data(self, conv_data_path):
        self.conversation_data = pd.read_csv(conv_data_path)
        model_data = self.conversation_data.drop('text', axis=1)
        return self

    def save_conversation_data(self, conv_data_path):
        self.conversation_data.to_csv(conv_data_path, index=False)
        return self

    def load_answer_list(self, answer_path):
        self.answer_list = pd.read_csv(answer_path)
        # TODO: check if "text" in columns here
        return self

    def update_conversation(self, message):
        sentences = message.split(".")
        self.conversation_data = self.conversation_data.append([{"message": s} for s in sentences], ignore_index=True)
        # self.nb_answers += 1
        return self

    def update_target_profile(self, target_profile):
        # TODO: check integrity of target profile
        self.target_profile = target_profile
        return self

    def update_response_strategy(self, strategy):
        # TODO: check if strategy is valid one
        self.response_strategy.strategy = strategy
        return self

    def get_answer(self):
        answer = self.response_strategy.select_answer(self.answer_list,
                                                      self.target_profile,
                                                      self.nb_answers)
        return answer


if __name__ == '__main__':
    import pytest
    pytest.main()

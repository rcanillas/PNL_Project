import pandas as pd
import random
from sklearn.neighbors import NearestNeighbors
import math
from collections import defaultdict

answ_list = pd.read_csv("templates/meta_answers.csv")
answ_corpus = answ_list.drop(["text"], axis=1)
nn_model = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(answ_corpus)


class ResponseStrategy:
    def __init__(self, strategy="random"):
        self.strategy = strategy
        self.previously_selected = defaultdict(list)

    def select_depth_answer(self, answer_list, depth_meter, target_profile):
        if depth_meter <= max(answer_list["depth"]):
            answers = answer_list.loc[answer_list["depth"] == depth_meter]["text"]
            # print(answers)
            answer = random.choice(answers.values)
            if answer not in self.previously_selected:
                self.previously_selected[depth_meter].append(answer)
            else:
                if len(self.previously_selected[depth_meter]) < len(answer_list):
                    answer = self.select_depth_answer(answer_list, depth_meter, target_profile)
                else:
                    answer = self.select_depth_answer(answer_list, depth_meter+1, target_profile)
        else:
            answer = "Je pense que nous avons fait le tour de la question ! Voici votre profil\n" + f"{target_profile}"
        return answer

    def select_answer(self, target_profile, nb_answers=0):
        answer = ""
        if self.strategy == "nearest_neighbors":
            answer_list = pd.read_csv("templates/meta_answers.csv")
            print(list(target_profile.values()))
            distances, indices = nn_model.kneighbors([list(target_profile.values())])
            ref_answer = indices[0][0]
            print(ref_answer, indices)
            answer = answer_list.iloc[ref_answer]['text']
            print(answer)
        if self.strategy == "depth_analysis":
            answer_list = pd.read_csv("templates/depth_answers.csv")
            depth_meter = math.floor((nb_answers-1)/3)
            answer = self.select_depth_answer(answer_list, depth_meter, target_profile)

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
        # model_data = self.conversation_data.drop('text', axis=1)
        return self

    def save_conversation_data(self, conv_data_path):
        self.conversation_data.to_csv(conv_data_path, index=False)
        return self

    def load_answer_list(self, answer_path):
        self.answer_list = pd.read_csv(answer_path)
        # TODO: check if "text" in columns here
        return self

    @staticmethod
    def _select_metaprogram(sentence_profile):
        metaprogram = None
        max_value = 0
        for key in sentence_profile.keys():
            metaprogram_score = sentence_profile[key]
            if abs(metaprogram_score) > 0:
                if abs(metaprogram_score) > max_value:
                    metaprogram_key = key.split("_")
                    if key != "ref_externe_interne":
                        metaprogram_neg = metaprogram_key[0]
                        metaprogram_pos = metaprogram_key[1]
                    else:
                        metaprogram_neg = metaprogram_key[1]
                        metaprogram_pos = metaprogram_key[2]
                    if metaprogram_score < 0:
                        metaprogram = metaprogram_neg
                    else:
                        metaprogram = metaprogram_pos
                    max_value = metaprogram_score
        return metaprogram, max_value

    def update_conversation(self, message, sentence_profile, inversion):
        sentences = message.split(".")
        metaprogram, metaprogram_score = self._select_metaprogram(sentence_profile)
        self.conversation_data = self.conversation_data.append([{"message": s, "type": "answer", "metaprogram": metaprogram, "metaprogram_score": metaprogram_score, "inversion": inversion}
                                                                for s in sentences], ignore_index=True)
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
        answer = self.response_strategy.select_answer(self.target_profile,
                                                      self.nb_answers)
        self.conversation_data = self.conversation_data.append([{"message": answer,
                                                                 "type": "question",
                                                                 "metaprogram": None}])
        return answer


if __name__ == '__main__':
    import pytest
    pytest.main()

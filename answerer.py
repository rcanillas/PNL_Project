import pandas as pd
import random


class ResponseStrategy:
    def __init__(self, strategy="random"):
        self.strategy = strategy

    def select_answer(self, answer_list, target_profile):
        if self.strategy == "random":
            return random.choice(answer_list["text"].values)


class Answerer:
    def __init__(self, session):
        self.session = session
        self.conversation_data = pd.DataFrame()
        self.response_strategy = ResponseStrategy()
        self.answer_list = pd.DataFrame()
        self.target_profile = None

    def load_conversation_data(self, conv_data_path):
        self.conversation_data = pd.read_csv(conv_data_path)
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
        answer = self.response_strategy.select_answer(self.answer_list, self.target_profile)
        return answer


if __name__ == '__main__':
    import pytest
    pytest.main()

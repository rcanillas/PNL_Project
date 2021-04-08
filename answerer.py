import pandas as pd
import pickle


class Answerer:

    def __init__(self, session):
        self.session = session
        self.conversation_data = pd.DataFrame()
        self.model = None

    def load_conversation_data(self, conv_data_path):
        self.conversation_data = pd.read_csv(conv_data_path)
        return self

    def save_conversation_data(self, conv_data_path):
        self.conversation_data.to_csv(conv_data_path, index=False)
        return self

    def load_model(self, model_path):
        self.model = pickle.loads(model_path)
        return self

    def get_message(self, message):
        sentences = message.split(".")
        self.conversation_data = self.conversation_data.append([{"message": s} for s in sentences], ignore_index=True)
        return self


if __name__ == '__main__':
    import pytest
    pytest.main()

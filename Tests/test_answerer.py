import pandas as pd
from answerer import Answerer
import pickle as pkl


class TestAnswerer:

    def test_create(self):
        ans = Answerer(1)
        assert ans.session == 1
        assert ans.conversation_data.equals(pd.DataFrame())
        assert ans.model is None

    def test_load_cv(self):
        test_df = pd.DataFrame([{"test": 1}, {"test": 2}])
        test_df.to_csv("test.csv", index=False)  # replace with IOStream to bypass file creation
        ans = Answerer(1)
        ans.load_conversation_data("test.csv")
        assert test_df.equals(ans.conversation_data)

    def test_save_cv(self):
        ans = Answerer(1)
        test_df = pd.DataFrame([{"test": 1}, {"test": 2}])
        ans.conversation_data = test_df
        ans.save_conversation_data("test.csv")
        test_df = pd.read_csv("test.csv")  # replace with IOStream to bypass file creation
        assert test_df.equals(ans.conversation_data)

    def test_load_model(self):
        ans = Answerer(1)
        model_pkl = pkl.dumps("test")
        ans.load_model(model_pkl)
        assert ans.model == "test"

    def test_get_message(self):
        ans = Answerer(1)
        message = "test message"
        test_df = pd.DataFrame([{"message": message}])
        ans.get_message(message)
        assert test_df.equals(ans.conversation_data)

    def test_get_message_sentences(self):
        ans = Answerer(1)
        message = "test message 1. test message 2"
        test_df = pd.DataFrame([{"message": s} for s in message.split(".")])
        ans.get_message(message)
        assert test_df.equals(ans.conversation_data)


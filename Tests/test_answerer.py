import pandas as pd
from answerer import Answerer


class TestAnswerer:

    def test_create(self):
        ans = Answerer(1)
        assert ans.session == 1
        assert ans.conversation_data.equals(pd.DataFrame())
        assert ans.response_strategy.strategy == "random"
        assert ans.answer_list.equals(pd.DataFrame())
        assert ans.target_profile is None

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

    def test_load_answer_list(self):
        test_df = pd.DataFrame([{"test": "hello"}, {"test": "world"}])
        test_df.to_csv("test.csv", index=False)  # replace with IOStream to bypass file creation
        ans = Answerer(1)
        ans.load_answer_list("test.csv")
        assert test_df.equals(ans.answer_list)

    def test_get_message(self):
        ans = Answerer(1)
        message = "test message"
        test_df = pd.DataFrame([{"message": message}])
        ans.update_conversation(message)
        assert test_df.equals(ans.conversation_data)

    def test_update_conversation_sentences(self):
        ans = Answerer(1)
        message = "test message 1. test message 2"
        test_df = pd.DataFrame([{"message": s} for s in message.split(".")])
        ans.update_conversation(message)
        assert test_df.equals(ans.conversation_data)

    def test_update_profile(self):
        ans = Answerer(1)
        profile = [0, 0, 0, 0]
        ans.update_target_profile(profile)
        assert ans.target_profile == profile

    def test_update_response_strategy(self):
        ans = Answerer(1)
        strategy = "opening"
        ans.update_response_strategy(strategy)
        assert ans.response_strategy.strategy == strategy

    def test_send_answer(self):
        ans = Answerer(1)
        test_ans_list = pd.DataFrame([{"text": "hello"}, {"text": "hello"}])
        ans.answer_list = test_ans_list
        answer = ans.get_answer()
        assert answer == "hello"

import json
meta_programs = ["test_1", "test_2"]


class Modeler:

    def __init__(self, target):
        self.target = target
        self.profile = {program: 0 for program in meta_programs}

    def __compute_profile(self, msg):
        print(msg)
        if "blip" in msg["message"]:
            self.profile["test_1"] += 1
        elif "blop" in msg["message"]:
            self.profile["test_2"] += 1
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

    def load_profile(self):
        return self

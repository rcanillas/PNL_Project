import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import floor
from collections import defaultdict
from fpdf import FPDF

brightness = 230
sns_palette = sns.color_palette("Paired", 12)
metaprogram_palette = [(c[0]*brightness, c[1]*brightness, c[2]*brightness) for c in sns_palette]
color_map = {"actif": metaprogram_palette[0],
             "passif": metaprogram_palette[1],
             "aller-vers": metaprogram_palette[2],
             "éviter-de": metaprogram_palette[3],
             "global": metaprogram_palette[4],
             "détail": metaprogram_palette[5],
             "externe": metaprogram_palette[6],
             "interne": metaprogram_palette[7],
             "similitude": metaprogram_palette[8],
             "difference": metaprogram_palette[9],
             "match": metaprogram_palette[10],
             "mismatch": metaprogram_palette[11],
             None: [0, 0, 0]}


class PdfExporter:

    def __init__(self, user_id, size=12):
        self.user_id = user_id
        self.user_name = self.user_id.split("_")[0]
        self.canvas = FPDF()
        # self.canvas = canvas.Canvas(f"user_data/{self.user_name}/conversation_report_{self.user_id}.pdf")
        self.size = size
        self.canvas.set_font("Courier", "", size=self.size)
        self.report_img = None

    def write_report(self, report_df):
        self.canvas.add_page()
        self.canvas.cell(60, 10, 'Rapport MetaSignature', 0, 1, 'C')
        if self.report_img is not None:
            self.canvas.image(self.report_img, w=floor(self.canvas.w - (self.canvas.w * 0.1)))
        y = 5
        for key in color_map.keys():
            if key is not None:
                color = color_map[key]
                self.canvas.set_text_color(r=color[0], g=color[1], b=color[2])
                self.canvas.cell(self.canvas.w - 2*self.canvas.l_margin, y, key)
                self.canvas.ln()
        self.canvas.add_page()
        y = 5
        for message in report_df.to_dict(orient="records"):
            text = message["message"] + "."
            if message["type"] == "question":
                suffix = "Q: "
                text = text[:-1]
            else:
                if message["inversion"]:
                    suffix = "A-!: "
                else:
                    suffix = "A: "
            color = color_map[message["metaprogram"]]

            self.canvas.set_text_color(r=color[0], g=color[1], b=color[2])
            self.canvas.multi_cell(self.canvas.w - 2*self.canvas.l_margin, y, suffix+text)
            self.canvas.ln()
        self.canvas.output(f"user_data/{self.user_name}/conversation_report_{self.user_id}.pdf")

    def generate_report_image(self, profile):
        profile_pd = pd.DataFrame()
        for key, value in profile.items():
            key_dict = {"metaprogam": key, "value": value}
            profile_pd = profile_pd.append([key_dict])
        print(profile_pd)
        plt.figure(figsize=(20, 10))
        sns.barplot(data=profile_pd, x="metaprogam", y="value", palette=sns_palette)
        plt.axhline(0, linestyle=":", color="grey")

        fig_path = f"user_data/{self.user_name}/metaprogram_report_{self.user_id}.png"
        plt.title(f"{self.user_name} MetaPrograms Overview")
        plt.savefig(fig_path, bbox_inches="tight")
        plt.show()
        plt.close()
        self.report_img = fig_path
        return fig_path

    def generate_flow_image(self, report_df):
        answ_df = report_df.loc[report_df["type"]=="answer"]
        flow_df = pd.DataFrame()
        mp_count = defaultdict(int)
        for msg_id, msg_info in enumerate(answ_df.to_dict(orient="records")):
            print(msg_info)
            mp_count[msg_info["metaprogram"]] += msg_info["metaprogram_score"]
            flow_dict = {"msg_id": msg_id,
                         "metaprogam": msg_info["metaprogram"],
                         "score": mp_count[msg_info["metaprogram"]]}
            flow_df = flow_df.append([flow_dict]).reset_index(drop=True)
        print(flow_df)
        plt.figure(figsize=(20, 10))
        sns.lineplot(data=flow_df, x="msg_id", y="score", hue="metaprogam",
                     linestyle=":", marker="o")
        plt.axhline(0, linestyle=":", color="grey")
        fig_path = f"user_data/{self.user_name}/metaprogram_flow_{self.user_id}.png"
        plt.title(f"{self.user_name} MetaPrograms Flow")
        plt.savefig(fig_path, bbox_inches="tight")
        plt.show()
        plt.close()


if __name__ == '__main__':
    text_df = pd.DataFrame([{'message': "test1", 'type': "question", "metaprogram": None},
                            {'message': "test2", 'type': "answer", 'metaprogram': "aller-vers"},
                            {'message': "test3", 'type': "answer", 'metaprogram': "éviter-de"}])
    text_export = PdfExporter('test')
    text_export.write_report(text_df)

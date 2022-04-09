import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import floor

from fpdf import FPDF

brightness = 230
sns_palette = sns.color_palette("Paired", 10)
metaprogram_palette = [(c[0]*brightness, c[1]*brightness, c[2]*brightness) for c in sns_palette]
color_map = {"actif": metaprogram_palette[0],
             "passif": metaprogram_palette[1],
             "aller-vers": metaprogram_palette[2],
             "éviter-de": metaprogram_palette[3],
             "global": metaprogram_palette[4],
             "specific": metaprogram_palette[5],
             "externe": metaprogram_palette[6],
             "interne": metaprogram_palette[7],
             "similitude": metaprogram_palette[8],
             "difference": metaprogram_palette[9],
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
        y = 10
        for key in color_map.keys():
            if key is not None:
                color = color_map[key]
                self.canvas.set_text_color(r=color[0], g=color[1], b=color[2])
                self.canvas.cell(self.canvas.w, y, key)
                self.canvas.ln()
        self.canvas.add_page()
        y = 10
        for message in report_df.to_dict(orient="records"):
            text = message["message"] + "."
            suffix = "Q: " if message["type"] == "question" else "A: "
            color = color_map[message["metaprogram"]]
            self.canvas.set_text_color(r=color[0], g=color[1], b=color[2])
            self.canvas.cell(self.canvas.w, y, suffix+text)
            self.canvas.ln()
        self.canvas.output(f"user_data/{self.user_name}/conversation_report_{self.user_id}.pdf", 'F')

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


if __name__ == '__main__':
    text_df = pd.DataFrame([{'message': "test1", 'type': "question", "metaprogram": None},
                            {'message': "test2", 'type': "answer", 'metaprogram': "aller-vers"},
                            {'message': "test3", 'type': "answer", 'metaprogram': "éviter-de"}])
    text_export = PdfExporter('test')
    text_export.write_report(text_df)

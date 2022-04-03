import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import floor

from fpdf import FPDF

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
        self.canvas.add_page()
        y = 10
        for message in report_df.to_dict(orient="records"):
            text = message["message"] + "."
            suffix = "Q: " if message["type"] == "question" else "A: "
            color = message["color"]
            self.canvas.cell(self.canvas.w, y, suffix+text)
            self.canvas.ln()
        self.canvas.output(f"user_data/{self.user_name}/conversation_report_{self.user_id}.pdf", 'F')

    def generate_report_image(self, profile):
        profile_pd = pd.DataFrame()
        for key, value in profile.items():
            key_dict = {"metaprogam": key, "value":value}
            profile_pd = profile_pd.append([key_dict])
        print(profile_pd)
        fig = plt.figure(figsize=(20, 10))
        ax1 = sns.barplot(data=profile_pd, x="metaprogam", y="value")
        plt.axhline(0, linestyle=":", color="grey")

        fig_path = f"user_data/{self.user_name}/metaprogram_report_{self.user_id}.png"
        plt.title(f"{self.user_name} MetaPrograms Overview")
        plt.savefig(fig_path, bbox_inches="tight")
        plt.show()
        plt.close()
        self.report_img = fig_path
        return fig_path


if __name__ == '__main__':
    text_df = pd.DataFrame([{'message':"test1",'type':"question",'color':"#000000"},
                            {'message':"test2",'type':"answer",'color':"#a6cfd5"}])
    text_export = PdfExporter('test')
    text_export.write_report(text_df)



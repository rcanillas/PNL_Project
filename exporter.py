import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns


class PdfExporter:

    def __init__(self, user_id, size=10):
        self.user_id = user_id
        self.canvas = canvas.Canvas(f"{user_id}.pdf")
        self.size = size
        self.canvas.setFont("Courier", self.size)

    def write_report(self, report_df):
        x = 1.3 * inch
        y = 11 * inch
        for message in report_df.to_dict(orient="records"):
            text = message["message"] + "."
            suffix = "Q: " if message["type"] == "question" else "A: "
            color = message["color"]
            self.canvas.setFillColor(color)
            self.canvas.drawString(x, y, suffix+text)
            y = y - self.size * 1.2
        self.canvas.showPage()
        self.canvas.save()

    def generate_report_image(self, profile):
        profile_pd = pd.DataFrame()
        for key, value in profile.items():
            key_dict = {"metaprogam": key, "value":value}
            profile_pd = profile_pd.append([key_dict])
        print(profile_pd)
        fig = plt.figure(figsize=(20, 10))
        ax1 = sns.barplot(data=profile_pd, x="metaprogam", y="value")
        plt.axhline(0, linestyle=":", color="grey")
        user_name = self.user_id.split("_")[0]
        fig_path = f"user_data/{user_name}/metaprogram_report_{self.user_id}.png"
        plt.savefig(fig_path, bbox_inches="tight")
        plt.show()
        plt.close()
        return fig_path


if __name__ == '__main__':
    text_df = pd.DataFrame([{'message':"test1",'type':"question",'color':"#000000"},
                            {'message':"test2",'type':"answer",'color':"#a6cfd5"}])
    text_export = PdfExporter('test')
    text_export.write_report(text_df)



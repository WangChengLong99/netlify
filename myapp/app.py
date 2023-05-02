from shiny import App, render, ui, reactive
import pandas as pd


app_ui = ui.page_fluid(
    ui.h1("pandas"),
    ui.input_text_area("data_path","输入数据路径","D://myblog/library/data/数据/学生.csv"),
    # 因为我们无法直接导入数据，所以输入数据路径后，手动的展示数据
    ui.input_action_button("show_data","生成数据"),
    ui.output_table("show_table")
)

def server(input, output, session):
    @reactive.Calc
    def get_data():
        return pd.read_csv(input.data_path())
    # @reactive.Effect
    # def get_data():
    #     pd.read_csv(input.data_path())
    @output
    @render.table
    @reactive.event(input.show_data)
    def show_table():
        data = get_data()
        return data.head(10)

app = App(app_ui, server)

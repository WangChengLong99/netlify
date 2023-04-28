from shiny import App, render, ui
import pandas as pd
import numpy as np

data = pd.Series([1,2,3])

app_ui = ui.page_fluid(
    ui.h2("Hello Shiny!"),
    ui.input_slider("n", "N", 0, 100, 20),
    ui.output_text_verbatim("txt"),
)

def server(input, output, session):
    @output
    @render.text
    def txt():
        return f"n*2+data[2] is {input.n() * 2 + data[2]}"


app = App(app_ui, server)

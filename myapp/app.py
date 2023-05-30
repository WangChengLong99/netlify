from shiny import App, render, ui, reactive
import pandas as pd

def df_to_ui_table(df,height):
    return ui.div(
            ui.tags.table(
                ui.tags.thead(
                    ui.tags.tr(
                        *[ui.tags.th(i,style="border: 1px solid #ddd;padding: 8px;text-align: left;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;  background-color: #f2f2f2;top: 0;z-index: 1;") for i in df.columns])
                ),
                ui.tags.tbody(
                *[ui.tags.tr(*[ui.tags.td(str(j),style="border: 1px solid #ddd;padding: 8px;text-align: left;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;") for j in df.loc[i,:]]) for i in df.index]
                ),
                style="border-collapse: collapse;min-width:100%;table-layout: fixed;"
                ),
            # ui.tags.script("""
            #     let el = null;
            #     let startX = null;
            #     let startWidth = null;
            #     document.querySelectorAll("th").forEach(th => {
            #     th.style.position = "relative";
            #     const grip = document.createElement("div");
            #     grip.innerHTML = "&nbsp;";
            #     grip.style.top = "0";
            #     grip.style.right = "0";
            #     grip.style.bottom = "0";
            #     grip.style.width = "5px";
            #     grip.style.position = "absolute";
            #     grip.style.cursor = "col-resize";
            #     grip.addEventListener("mousedown", e => {
            #         el = e.target.parentElement;
            #         startX = e.pageX;
            #         startWidth = el.offsetWidth;
            #     });
            #     th.appendChild(grip);
            #     });
            #     document.addEventListener("mousemove", e => {
            #     if (el) {
            #         const width = startWidth + (e.pageX - startX);
            #         el.style.width = width + "px";
            #     }
            #     });
            #     document.addEventListener("mouseup", () => {
            #     el = null;
            #     startX = null;
            #     startWidth = null;
            #     });
            # """
            # ),    
            style = f"overflow-x: auto;overflow-y: scroll;max-height:{height}px;min-width:100%;margin-bottom: 1em;"   
        )

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file("data","选择数据",multiple=False,),
            ui.input_selectize("sort","排序",[],multiple=True),
            ui.input_checkbox("ad","升序",True)
        ),
        ui.panel_main(
            ui.output_ui("show_data")
        )
        ),
    title="pandas",
)

def server(input, output, session):
    # 表格需要时常被调用，需要保持cached
    @reactive.Calc
    def get_data():
        if input.data():
            return pd.read_csv(input.data()[0]["datapath"])
    # 显示表格，并且可排序    
    @output
    @render.ui()
    def show_data():
        if input.data():
            df = get_data()
            df100 =df.sort_values(by=list(input.sort()),ascending=input.ad()).head(100) if input.sort() else df.head(100)
            return df_to_ui_table(df100,300)
    # 根据data更新字段    
    @reactive.Effect()   
    def _():
        if input.data():
            df = get_data()
            return ui.update_selectize(
                "sort",
                label="排序",
                choices = list(df.columns)
                )
app = App(app_ui, server)

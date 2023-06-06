from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Simhei']; #SimHei黑体 
plt.rcParams['axes.unicode_minus']=False; #正常显示图中负号

styles = {
    "table_container_div" : "overflow-x: auto;overflow-y: scroll;max-height:{}px;min-width:100%;", 
    "table" : "border-collapse: collapse;min-width:100%;table-layout: fixed;",    
    "th" : "border: 1px solid #ddd;padding: 8px;text-align: left;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;  background-color: #f2f2f2;top: 0;z-index: 1;",
    "td" : "border: 1px solid #ddd;padding:8px;text-align: left;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;",
    "ui_nolabel_td" : "border: 1px solid #ddd;display:inline-block;padding:3px;height:41px;white-space: nowrap;min_width:100px;",
    "ui_container_td" : "border: 1px solid #ddd;display:inline-block;padding:3px;max-height:70px;white-space: nowrap;min_width:100px;",
    "button" : "background-color:rgb(121, 188, 229);color:white;"
}

def df_to_ui_table(df,height,index_con=False):
    return ui.div(
            ui.tags.table(
                ui.tags.thead(
                    ui.tags.tr(
                        *[ui.tags.th(i,style=styles["th"]) for i in list(df.index.names if index_con else [])+list(df.columns)])
                ),
                ui.tags.tbody(
                    *[ui.tags.tr(*[ui.tags.td(str(j),style=styles["td"]) for j in (list(i if isinstance(i,tuple) else [i]) if index_con else [])+df.loc[i,:].to_list()]) for i in df.index]
                ),
                style = styles["table"]
                ),
            style = styles["table_container_div"].format(height)   
        )

def data_summary(data):
    def 缺失值(x):
        return x.isnull().sum()
    def 缺失比例(y):
        return f"{round(y.isnull().sum()/len(y),2)*100}%"
    def 数据类型(z):
        return z.dtypes
    df1 = pd.DataFrame([["行数",data.shape[0]],["列数",data.shape[1]],['重复数',data.duplicated().sum()]])
    df = data.agg([缺失值,缺失比例,数据类型]).T.reset_index(names="字段")
    summary_info = ui.div(
                        ui.tags.table(
                            *[ui.tags.tr(*[ui.tags.td(str(j),style=styles["td"]) for j in df1.loc[i,:]]) for i in df1.index],
                            style = styles["table"]
                            ),
                        style = styles["table_container_div"].format(130)
                )
    return ui.div(summary_info,df_to_ui_table(df,350))

def ui_table(col_num,height=300,*tagchild):
    row,mod = divmod(len(tagchild),col_num)
    return ui.div(
                ui.tags.table(
                    *[ui.tags.tr(ui.tags.td(tagchild[2*r][0],tagchild[2*r][1],style=styles["ui_container_td"]),ui.tags.td(tagchild[2*r+1][0],tagchild[2*r+1][1],style=styles["ui_container_td"])) for r in range(row)],
                    ui.tags.tr(*[ui.tags.td(u[0],u[1],style=styles["ui_container_td"]) for u in tagchild[-mod:]]) if mod > 0 else None,
                    style = styles["table"]
                    ),
                style = styles["table_container_div"].format(height)
            ),

dimension_describe_height = 300
dimension_value_count_height = 200
value_describe_height = 200
value_plot_height = "200px"

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            4,
            ui.navset_tab_card(
                ui.nav(
                    "数据源",
                    ui.input_file("data","导入数据",accept=[".csv",".xlsx"],placeholder="选择csv或excel文件",multiple=True),
                    ui.navset_tab(
                        ui.nav("总体",ui.output_ui("info_pop")),
                        ui.nav(
                            "维度",
                            ui.output_ui("dimension"),
                            ui.output_ui("info_dimension")),
                        ui.nav(
                            "度量",
                            ui.output_ui("value"),
                            ui.output_ui("info_value"),
                            ui.output_plot("plot_value",height=value_plot_height)),
                    ),
                    ),
                ui.nav(
                    "数据清洗",
                    ui.column(
                        12,
                        ui.navset_tab(
                            ui.nav("类型转换",
                                   ui.column(
                                        12, 
                                        ui.output_ui("field_dtype"),
                                        ui.input_action_button("changedtype","改变类型",style=styles["button"]),
                                        style = "height:600px"
                                   )
                            ),
                            ui.nav("缺失值处理",
                                   ui.column(
                                        12,
                                        ui.output_ui("field_na"),
                                        style = "height:600px",
                                   )
                            )
                        )
                    )
                    ),       
            ),
        ),
        ui.column(
            8,
            ui.row(
                ui.column(
                        5,
                        ui.output_ui("create_graph_ui"),
                        style = "height:310px"
                ),
                ui.column(
                        7,
                        ui.output_plot("show_graph"),
                        style = "height:310px"
                )
    ),
            ui.row(
                ui.navset_tab_card(
                    ui.nav("数据",ui.output_ui("show_data")),
                    ui.nav("表连接",
                           ui.row(
                                ui.column(
                                        5,
                                        ui.output_ui("create_merge_ui"),
                                        style = "height:350px"
                                ),
                                ui.column(
                                        7,
                                        ui.output_ui("show_merge_data"),
                                        style = "height:350px"
                                )
                           )
                    ),
                    ui.nav("透视表",
                           ui.row(
                                ui.column(
                                        5,
                                        ui.output_ui("create_pivot_ui"),
                                        style = "height:350px"
                                ),
                                ui.column(
                                        7,
                                        ui.output_ui("show_pivot_data"),
                                        style = "height:350px"
                                )
                           )
                           ),
                    ui.nav("groupby",
                           ui.row(
                                ui.column(
                                        5,
                                        ui.output_ui("create_groupby_ui"),
                                        style = "height:350px"
                                ),
                                ui.column(
                                        7,
                                        ui.output_ui("show_groupby_data"),
                                        style = "height:350px"
                                )
                           )                           
                           ),
                ),
            )
            )
    )        
)

def server(input,output,session):
    merge_data = reactive.Value({})
    pivot_data = reactive.Value({})
    groupby_data = reactive.Value({})

    #################  数据导入呈现模块 ######################

    ## 导入数据，数据保持为calc状态,返回数据为name:data的字典形式
    @reactive.Calc
    def get_data():
        if input.data():
            name_data = {i["name"].replace(".csv","") if i["name"].endswith(".csv") else i["name"].replace(".xlsx","") : pd.read_csv(i["datapath"]) if i["name"].endswith(".csv") else pd.read_excel(i["datapath"]) for i in input.data()}
            return name_data

    ## 获取当前标签页数据    
    @reactive.Calc
    def selected_data():
        if input.data():
            if input.dataname() in get_data().keys():
                return get_data()[input.dataname()]

    ## 以标签页展示所有数据
    @output
    @render.ui
    def show_data():
        if input.data():
            ds = get_data()
            return ui.navset_tab(
                    *[ui.nav(k,df_to_ui_table(v.head(100),300)) for k,v in ds.items()],
                    id="dataname"
                )

    ######################### 数据信息呈现 ############################

    ## 展示汇总信息
    @output
    @render.ui
    def info_pop():
        if isinstance(selected_data(), pd.DataFrame):
            return data_summary(selected_data())
    
    ## 维度字段
    @output
    @render.ui
    def dimension():
        if isinstance(selected_data(), pd.DataFrame):
            return ui.input_selectize("dm","度量",choices=list(selected_data().select_dtypes(exclude=["number"]).columns))
    
    ## 展示维度信息
    @output
    @render.ui
    def info_dimension():
        if isinstance(selected_data(), pd.DataFrame):
            if (bool(input.dm()))&(input.dm() in selected_data().columns):
                data = selected_data()[[input.dm()]]
                return ui.div(
                    data.describe().reset_index(names="指标").pipe(df_to_ui_table,dimension_describe_height),
                    data.value_counts().to_frame().reset_index(names="取值").pipe(df_to_ui_table,dimension_value_count_height)) 

    ## 度量字段
    @output
    @render.ui
    def value():
        if isinstance(selected_data(), pd.DataFrame):
            return ui.input_selectize("vl","度量",choices=list(selected_data().select_dtypes(include=["number"]).columns))
    
    ## 展示度量信息
    @output
    @render.ui
    def info_value():
        if isinstance(selected_data(), pd.DataFrame):
            if (bool(input.vl()))&(input.vl() in selected_data().columns):
                data = selected_data()[[input.vl()]]
                return data.describe().reset_index(names="指标").pipe(df_to_ui_table,value_describe_height)

    ## 展示度量分布
    @output
    @render.plot
    def plot_value():
        if isinstance(selected_data(), pd.DataFrame):
            if (bool(input.vl()))&(input.vl() in selected_data().columns):
                data = selected_data()[input.vl()]
                fig,ax = plt.subplots(1,1)
                ax.hist(
                x=data,
                ##箱子数(bins)设置，以下三种不能同时并存
                #bins=20,#default: 10
                #bins=[4,6,8],#分两个箱子，边界分别为[4,6),[6,8]
                bins='auto',# 可选'auto', 'fd', 'doane', 'scott', 'stone', 'rice', 'sturges', or 'sqrt'.
                #选择最合适的bin宽，绘制一个最能反映数据频率分布的直方图 

                #range=(5,7),#最左边和最右边箱子边界，不指定时，为(x.min(), x.max())
                density=True, #默认为False，y轴显示频数；为True y轴显示频率，频率统计结果=该区间频数/(x中总样本数*该区间宽度)
                #weights=np.random.rand(len(x)),#对x中每一个样本设置权重，这里随机设置了权重
                cumulative=False,#默认False，是否累加频数或者频率，及后面一个柱子是前面所有柱子的累加
                bottom=0,#设置箱子y轴方向基线，默认为0，箱子高度=bottom to bottom + hist(x, bins)
                histtype='bar',#直方图的类型默认为bar{'bar', 'barstacked', 'step', 'stepfilled'}
                align='mid',#箱子边界值的对齐方式，默认为mid{'left', 'mid', 'right'}
                orientation='vertical',#箱子水平还是垂直显示，默认垂直显示('vertical')，可选'horizontal'
                rwidth=1.0,#每个箱子宽度，默认为1，此时显示50%
                log=False,#y轴数据是否取对数，默认不取对数为False
                label=input.vl(),#图例
                #normed=0,#功能和density一样，二者不能同时使用
                facecolor='blue',#箱子颜色 
                edgecolor="black",#箱子边框颜色
                stacked=False,#多组数据是否堆叠
                alpha=0.5#箱子透明度
                )
                return fig

    ############################## 数据清洗 ##########################

    # 展示数据类型并且可更改
    @output
    @render.ui
    def field_dtype():
        if isinstance(selected_data(), pd.DataFrame):
            d1 = selected_data().dtypes.reset_index()
            d1.columns = ["字段","数据类型"]
            dtype_info = ui.div(
            ui.tags.table(
                ui.tags.thead(
                    ui.tags.tr(
                        ui.tags.th("字段",style=styles["th"]),
                        ui.tags.th("数据类型",style=styles["th"]+"width:100px;")#和下面的ui的width保持一致。
                        )
                ),
                ui.tags.tbody(
                *[ui.tags.tr(
                    ui.tags.td(d1.loc[i,"字段"],style=styles["td"]),
                    ui.tags.td(ui.input_selectize(d1.loc[i,"字段"]+"dtype",None,choices=["int32","int64","number","object","string","bool","datetime64","float64"],selected=d1.loc[i,"数据类型"],width="100px"),style=styles["ui_nolabel_td"])
                    ) for i in d1.index],
                ),
                    style = styles["table"]
            ),
                style = styles["table_container_div"].format(550)
            )
            return dtype_info

    # 展示缺失类型并且可更改
    @output
    @render.ui
    def field_na():
        if isinstance(selected_data(), pd.DataFrame):
            d1 = selected_data().apply(lambda y:f"{round(y.isnull().sum()/len(y),2)*100}%").reset_index()
            d1.columns = ["字段","缺失比例"]
            d1 = d1[d1["缺失比例"].str.replace("%","").map(float)>0].sort_values(by="缺失比例",key = lambda x: x.str.replace("%","").map(float),ascending=False)
            return  ui.div(
            ui.tags.table(
                ui.tags.thead(
                    ui.tags.tr(
                        *[ui.tags.th(i,style=styles["th"]) for i in d1.columns],
                        ui.tags.th("处理缺失值",style=styles["th"]+"width:100px;")#和下面保持一致
                        )
                ),
                ui.tags.tbody(
                *[ui.tags.tr(
                    ui.tags.td(d1.loc[i,"字段"],style=styles["td"]),
                    ui.tags.td(d1.loc[i,"缺失比例"],style=styles["td"]),
                    ui.tags.td(ui.input_selectize(d1.loc[i,"字段"]+"na",None,choices=[""],selected="",width="100px"),style=styles["ui_nolabel_td"])
                    ) for i in d1.index],
                ),
                    style = styles["table"]
            ),
                style = styles["table_container_div"].format(590)
            )
        
    # 修改数据类型   
    @reactive.Effect
    @reactive.event(input.changedtype)
    def change_field_dtype():
        if isinstance(selected_data(), pd.DataFrame):
            for col in selected_data().columns:
                # 注意下面不能写eval("input."+col+"dtype()"),input会默认为内置函数
                if selected_data()[col].dtypes != input[col+"dtype"]():
                    selected_data().loc[:,col] = selected_data()[col].astype(input[col+"dtype"]())
            ui.update_selectize("dm",label="维度",choices=list(selected_data().select_dtypes(exclude=["number"]).columns))
            ui.update_selectize("vl",label="度量",choices=list(selected_data().select_dtypes(include=["number"]).columns))

    # 修改缺失类型

    ####################### merge_data ############################

    # 创建连接表的ui
    @output
    @render.ui
    def create_merge_ui():
        if get_data():
            return ui_table(
                        2,340,  
                        ["左连接表" , ui.input_selectize("table_left",None,width="150px",
                        choices=[k for k in get_data().keys()],selected=None)],
                        ["右连接表" , ui.input_selectize("table_right",None,width="150px",
                        choices=[k for k in get_data().keys()],selected=None)],
                        ["左连接列" , ui.input_selectize("left_on_col",None,[],multiple=True,width="150px")],
                        ["右连接列" , ui.input_selectize("right_on_col",None,[],multiple=True,width="150px")],
                        ["左保留列" , ui.input_selectize("left_save_col",None,[],multiple=True,width="150px")],
                        ["右保留列" , ui.input_selectize("right_save_col",None,[],multiple=True,width="150px")],
                        ["连接方式" , ui.input_selectize("merge_way",None,width="150px",
                        choices=["left","right","outer","inner","cross"])],
                        ["表名" , ui.input_text("merge_table_name",None,"",width="150px")],
                        ["",ui.input_action_button("cod_merge_table_button","增删表格",style=styles["button"],width="150px")],
                        ["选择删除表格",ui.input_selectize("delete_merge_name",None,[],multiple=True,width="150px")],
                        )

    # 根据表更新字段
    @reactive.Effect
    def _():
        if isinstance(get_data(),dict):
            if (bool(input.table_left()))&(input.table_left() in list(get_data().keys())):
                ui.update_selectize("left_on_col",label=None,choices=list(get_data()[input.table_left()].columns))
                ui.update_selectize("left_save_col",label=None,choices=list(get_data()[input.table_left()].columns))
            if (bool(input.table_right()))&(input.table_right() in list(get_data().keys())):
                ui.update_selectize("right_on_col",label=None,choices=list(get_data()[input.table_right()].columns))
                ui.update_selectize("right_save_col",label=None,choices=list(get_data()[input.table_right()].columns))   

    # 更新merge数据
    @reactive.Effect
    @reactive.event(input.cod_merge_table_button)
    def update_merge_data():
        if not bool(input.delete_merge_name()):
            data = pd.merge(
                left=get_data()[input.table_left()],
                right=get_data()[input.table_right()],
                on = None if list(input.left_on_col()) != list(input.right_on_col()) else list(input.left_on_col()),
                left_on=list(input.left_on_col()) if list(input.left_on_col()) != list(input.right_on_col()) else None,
                right_on=list(input.right_on_col()) if list(input.left_on_col()) != list(input.right_on_col()) else None,
                how =  input.merge_way(),
            )[list(input.left_save_col())+list(input.right_save_col())]
            md_value = merge_data.get().copy()
            md_value.update({input.merge_table_name():data})
            merge_data.set(md_value)
            ui.update_selectize("delete_merge_name",label=None,choices=list(merge_data.get().keys())+["清空"],selected=None)
        else:
            if "清空" in input.delete_merge_name():
                merge_data.set({})
                ui.update_selectize("delete_merge_name",label=None,choices=[],selected=None)
            else:
                md_value = merge_data.get().copy()
                for i in input.delete_merge_name():
                    md_value.pop(i)
                merge_data.set(md_value)
                if merge_data.get():
                    ui.update_selectize("delete_merge_name",label=None,choices=list(merge_data().keys())+["清空"],selected=None)
                else:
                    ui.update_selectize("delete_merge_name",label=None,choices=[],selected=None)
                    
    # 以标签页展示merge_data
    @output
    @render.ui
    # @reactive.event(input.cod_merge_table_button)
    def show_merge_data():
        if merge_data.get():
            ds = merge_data.get()
            return ui.navset_tab(*[ui.nav(k,df_to_ui_table(v.head(100),300)) for k,v in ds.items()])

    ################################## pivot_table ##########################

    # 创建pivot_table的ui
    @output
    @render.ui
    def create_pivot_ui():
        return ui_table(2,340,
            ["选择表格",ui.input_selectize("select_merge_and_data_table",None,
                choices = list(get_data().keys() if get_data() else [])  + list(merge_data.get().keys() if merge_data.get() else []),width="150px")],
            ["index",ui.input_selectize("pivot_index_col",None,multiple=True,
                choices=[],width="150px")],
            ["column",ui.input_selectize("pivot_column_col",None,[],multiple=True,width="150px")],
            ["值",ui.input_selectize("pivot_value_col",None,[],multiple=True,width="150px")],
            ["函数",ui.input_selectize("pivot_value_func",None,["sum","mean","max","min","count"],width="150px")],
            # ["填充缺失值",ui.input_text("fill_pivot_na",None,None)] ,
            ["表名" , ui.input_text("pivot_table_name",None,"",width="150px")],
            ["选择删除表格",ui.input_selectize("delete_pivot_name",None,[],multiple=True,width="150px")],
            ["",ui.input_action_button("cod_pivot_table_button","增删表格",style=styles["button"],width="150px")],
                        )
    
    # 根据表格更新字段
    @reactive.Effect()
    def update_pivot_ui():
        if input.select_merge_and_data_table():
            c = list(get_data()[input.select_merge_and_data_table()].columns) if input.select_merge_and_data_table() in list(get_data().keys()) else list(merge_data.get()[input.select_merge_and_data_table()].columns)
            ui.update_selectize("pivot_index_col",label=None,choices=c)
            ui.update_selectize("pivot_column_col",label=None,choices=c)
            ui.update_selectize("pivot_value_col",label=None,choices=c)

    # 更新pivot_data
    @reactive.Effect
    @reactive.event(input.cod_pivot_table_button)
    def update_pivot_data():
        if not bool(input.delete_pivot_name()):
            if input.pivot_value_func():
                func_map = {"sum":sum,"mean":lambda x: round(sum(x)/len(x),2),"max":max,"min":min,"count":len}
                data = pd.pivot_table(
                    merge_data.get()[input.select_merge_and_data_table()] if input.select_merge_and_data_table() in list(merge_data.get().keys()) else get_data()[input.select_merge_and_data_table()],
                    index = list(input.pivot_index_col()),
                    columns = list(input.pivot_column_col()),
                    values =list(input.pivot_value_col()),
                    aggfunc= func_map[input.pivot_value_func()]
                )
            else :
                data = pd.pivot(
                    merge_data.get()[input.select_merge_and_data_table()] if input.select_merge_and_data_table() in list(merge_data.get().keys()) else get_data()[input.select_merge_and_data_table()],
                    index = list(input.pivot_index_col()),
                    columns = list(input.pivot_column_col()),
                    values =list(input.pivot_value_col()),
                )    
            pivot_value = pivot_data.get().copy()
            pivot_value.update({input.pivot_table_name():data})
            pivot_data.set(pivot_value)
            ui.update_selectize("delete_pivot_name",label=None,choices=list(pivot_data.get().keys())+["清空"],selected=None)
        else:
            if "清空" in input.delete_pivot_name():
                pivot_data.set({})
                ui.update_selectize("delete_pivot_name",label=None,choices=[],selected=None)
            else:
                pivot_value = pivot_data.get().copy()
                for i in input.delete_pivot_name():
                    pivot_value.pop(i)
                pivot_data.set(pivot_value)
                if pivot_data.get():
                    ui.update_selectize("delete_pivot_name",label=None,choices=list(pivot_data().keys())+["清空"],selected=None)
                else:
                    ui.update_selectize("delete_pivot_name",label=None,choices=[],selected=None)
                        
    # 展示pivot_table
    @output
    @render.ui
    def show_pivot_data():
        if pivot_data.get():
            ds = pivot_data.get()
            return ui.navset_tab(*[ui.nav(k,df_to_ui_table(v.head(100),300,True)) for k,v in ds.items()])
    
    ######################### groupby_data ########################

    # 创建连接表的ui
    @output
    @render.ui
    def create_groupby_ui():
        return ui_table(
                    2,340,  
                    ["选择表格",ui.input_selectize("smadt",None,
                    choices =list(get_data().keys() if get_data() else [])  + list(merge_data.get().keys() if merge_data.get() else []),width="150px")],
                    ["分组列",ui.input_selectize("groupby_index_col",None,multiple=True,
                        choices=[],width="150px")],
                    ["保留列",ui.input_selectize("groupby_column_col",None,[],multiple=True,width="150px")],
                    ["函数选项",ui.input_selectize("groupby_func_kind",None,["行","列","group"],width="150px")],
                    ["函数",ui.input_selectize("groupby_func_option",None,["sum","mean","max","min","count"],width="150px")],
                    ["表名" , ui.input_text("groupby_table_name",None,"",width="150px")],
                    ["选择删除表格",ui.input_selectize("delete_groupby_name",None,[],multiple=True,width="150px")],
                    ["",ui.input_action_button("cod_groupby_table_button","增删表格",style=styles["button"],width="150px")],
                    )

    # 根据表更新字段
    @reactive.Effect
    def update_groupby_ui():
        if input.smadt():
            c = list(get_data()[input.smadt()].columns) if input.smadt() in list(get_data().keys()) else list(merge_data.get()[input.smadt()].columns)
            ui.update_selectize("groupby_index_col",label=None,choices=c)
            ui.update_selectize("groupby_column_col",label=None,choices=c)

    # 更新groupby_data数据
    @reactive.Effect
    @reactive.event(input.cod_groupby_table_button)
    def update_groupby_data():
        if not bool(input.delete_groupby_name()):
            func_map = {"sum":np.sum,"mean":np.mean,"median":np.median,"max":np.amax,"min":np.amin,"count":lambda x:len(x) if len(x.shape)==1 else x.shape[0]*x.shape[1]}
            data = merge_data.get()[input.smadt()] if input.smadt() in list(merge_data.get().keys()) else get_data()[input.smadt()]
            new_data = data.groupby(list(input.groupby_index_col()))[list(input.groupby_column_col())]
            #下面都是以单个函数为判断标准
            if input.groupby_func_kind() == "行":
                new_data2 = new_data.apply(func_map[input.groupby_func_option()],axis=1)
                new_data2.columns = [input.groupby_func_option()]
            else:
                if input.groupby_func_kind() == "列":
                    new_data2 = new_data.agg(func_map[input.groupby_func_option()])
                # 还有group没有写
            groupby_value = groupby_data.get().copy()
            groupby_value.update({input.groupby_table_name():new_data2})
            groupby_data.set(groupby_value)
            ui.update_selectize("delete_groupby_name",label=None,choices=list(groupby_data.get().keys())+["清空"],selected=None)
        else:
            if "清空" in input.delete_groupby_name():
                groupby_data.set({})
                ui.update_selectize("delete_groupby_name",label=None,choices=[],selected=None)
            else:
                groupby_value = groupby_data.get().copy()
                for i in input.delete_groupby_name():
                    groupby_value.pop(i)
                groupby_data.set(groupby_value)
                if groupby_data.get():
                    ui.update_selectize("delete_groupby_name",label=None,choices=list(groupby_data().keys())+["清空"],selected=None)
                else:
                    ui.update_selectize("delete_groupby_name",label=None,choices=[],selected=None)
                    
    # 以标签页展示groupby_data
    @output
    @render.ui
    def show_groupby_data():
        if groupby_data.get():
            ds = groupby_data.get()
            return ui.navset_tab(*[ui.nav(k,df_to_ui_table(v.head(100),300,True)) for k,v in ds.items()])
    
    ############################# graph ##############################

    #创建graph_ui
    @output
    @render.ui
    def create_graph_ui():
        return ui.div(
        ui.input_selectize("graph_table","选择表格",choices=list(groupby_data.get().keys()),width="150px"),
        ui.input_action_button("cod_graph_button","生成图片",width="150px")
        )
    
    # 展示图表
    @output
    @render.plot
    @reactive.event(input.cod_graph_button)    
    def show_graph():
        if input.graph_table():
            fig,ax = plt.subplots(1,1)
            groupby_data.get()[input.graph_table()].plot(
                kind="bar",
                ax = ax
            )
            return fig
    
    # 创建pivot_table()

app = App(app_ui,server)

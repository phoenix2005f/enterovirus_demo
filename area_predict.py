
# coding: utf-8

# In[106]:


import pandas as pd
import numpy as np
from random import randint

from bokeh.models import Plot
from bokeh.embed import components
from bokeh.models import (
    GeoJSONDataSource,
    HoverTool,
    LinearColorMapper,
    CategoricalColorMapper
)
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.layouts import column,row
from bokeh.models import ColumnDataSource,Range1d
import json
from bokeh.io import show, output_notebook, output_file
from bokeh.models import TapTool,HoverTool,RangeTool
# from bokeh.models import HoverTool
from bokeh.models.glyphs import Patches
from bokeh.models.widgets import CheckboxGroup,PreText,DataTable, TableColumn
from bokeh.layouts import widgetbox


TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"


def output_res():

    with open(r'./twgeo_easy_rates.json', 'r') as file:
        json_str = file.read()
        geo_source = GeoJSONDataSource(geojson=json_str)
        twgeo_json = json.loads(json_str)

  


    pred_4week = pd.read_csv('prediction_4week.csv')




    areas = ['南區','北區','東區','高屏區','台北區','中區']
    models=['CatBoost','XGB','ConvLSTM','GRU','LGBM','truth']

    color_list=['black','red','blue','green','cyan','purple']




    area_dict={}
    for idx,area in enumerate(areas):
        area_dict[area]={}

        temp=pd.read_csv('./data/{}.csv'.format(area))
        area_dict[area]['df'] = temp
        area_dict[area]['DT'] = pd.to_datetime(temp['DT'].values)
        area_idx = []
        for i in range(22):
            if twgeo_json['features'][i]['properties']['area']==area:
                area_idx.append(i)
        area_dict[area]['area_idx']=area_idx



    def fig_config(fig):
        fig.grid.grid_line_color = None
        fig.toolbar.logo = None
        fig.toolbar_location = None
        fig.legend.location = "top_left"
        fig.legend.click_policy = "hide"
        fig.xaxis.axis_label = 'Date'
        fig.yaxis.axis_label = '腸病毒人數'


    future_4_weeks = []
    data_dict = {}
    model_cds = {}

    pred_4week = pd.read_csv('prediction_4week.csv')

    pred_64week = pd.read_csv('prediction_64week.csv')

    pred_4week_mae = pd.read_csv('mae_4week.csv')
    pred_64week_mae = pd.read_csv('mae_64week.csv')

    for area in areas:
        for model in models:
            data_dict['{}_{}_4week'.format(area,model)] = pred_4week['{}_{}'.format(area,model)].values
            data_dict['{}_{}_64week'.format(area,model)] = pred_64week['{}_{}'.format(area,model)].values
            data_dict['{}_{}_4week_mae'.format(area,model)] = pred_4week_mae


    data_dict['x_4week'] = pd.to_datetime(pred_4week['x'].values)
    data_dict['x_64week'] = pd.to_datetime(pred_64week['x'].values)
    dates = data_dict['x_64week']


    fig_predict = figure(title="predictions", tools=TOOLS, width=600, height=300,x_axis_type='datetime')


    mae_source_4week = ColumnDataSource(data=dict())
    mae_source_64week = ColumnDataSource(data=dict())
    columns = [
        TableColumn(field="model", title="model Name"),
        TableColumn(field="mae", title="MAE")
    ]



    data_table_4week = DataTable(source=mae_source_4week, columns=columns, width=800)
    data_table_64week = DataTable(source=mae_source_64week, columns=columns, width=800)


    stats_4week = PreText(text='',width=500)
    stats_64week = PreText(text='',width=500)



    fig_predict_1year = figure(title="predictions_1year", tools=TOOLS, width=1000, height=300,x_axis_type='datetime',
                              x_axis_location="above",background_fill_color="#efefef", x_range=(dates[0], dates[20]))


    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    plot_height=130, plot_width=1000, y_range=fig_predict_1year.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color="#efefef")

    range_rool = RangeTool(x_range = fig_predict_1year.x_range)
    range_rool.overlay.fill_color = "navy"
    range_rool.overlay.fill_alpha = 0.2



    for i,model in enumerate(models):
        model_cds[model] = {}
        model_cds[model]['cds_4week'] = ColumnDataSource(data={'x':[],'y':[]})
        model_cds[model]['cds_64week'] = ColumnDataSource(data={'x':[],'y':[]})

        fig_predict.line(x='x',y='y',source=model_cds[model]['cds_4week'],line_color=color_list[i],muted_color=color_list[i],line_width=2,line_alpha=0.7,legend=model)

        fig_predict_1year.line(x='x',y='y',source = model_cds[model]['cds_64week'],line_color=color_list[i],muted_color=color_list[i],line_width=2,line_alpha=0.7,legend=model)
        select.line('x', 'y', source = model_cds[model]['cds_64week'],line_color=color_list[i],muted_color=color_list[i])


    select.ygrid.grid_line_color = None
    select.add_tools(range_rool)
    select.toolbar.active_multi = range_rool
 

    fig_config(fig_predict)
    fig_config(fig_predict_1year)


    p = figure(title="Taiwan(請點擊地圖以檢視分區 mae)", tools=TOOLS, x_axis_location=None, y_axis_location=None, width=600, height=800)
    p.background_fill_color = 'beige'
    p.border_fill_color = 'black'
    p.border_fill_alpha = 0.05
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    p.toolbar_location = None    

    for i in range(22):    
        twgeo_json['features'][i]['properties']['line_width'] = 0.5
        twgeo_json['features'][i]['properties']['line_color'] = 'white'

    geo_source.geojson = json.dumps(twgeo_json)    

    selected_g = Patches(fill_color='blue',line_color='white', line_width=4,line_alpha=0.5)


    renderer = p.patches('xs', 'ys', fill_alpha=0.7,fill_color='blue',line_color='line_color', line_width='line_width',line_alpha=1,source=geo_source)
    renderer.selection_glyph = selected_g

    p.add_tools(TapTool())
    p.add_tools(HoverTool(tooltips=[("name", "@name"),("index","$index"),("(Lon,Lat)", "($x, $y)")]))


    def my_tap_handler(attr,old,new):



        fig_config(fig_predict)

        idx=geo_source.selected.indices[0]


        area = twgeo_json['features'][idx]['properties']['area']


        geo_source.selected.indices = area_dict[area]['area_idx']


        for i in range(22):
            if twgeo_json['features'][i]['properties']['area']==area:
                twgeo_json['features'][i]['properties']['line_width']=4
                twgeo_json['features'][i]['properties']['line_color']='black'

            else:
                twgeo_json['features'][i]['properties']['line_width']=0.5
                twgeo_json['features'][i]['properties']['line_color']='white'

        geo_source.geojson = json.dumps(twgeo_json)

        if area:

            temp_date_4week = data_dict['x_4week']
            temp_date_64week = data_dict['x_64week']
            temp_text_4week =''

            for i,model in enumerate(models):
                temp_y_4week = data_dict['{}_{}_4week'.format(area,model)]
                temp_y_64week = data_dict['{}_{}_64week'.format(area,model)]

                model_cds[model]['cds_4week'].data = {'x':temp_date_4week,'y':temp_y_4week}
                model_cds[model]['cds_64week'].data = {'x':temp_date_64week,'y':temp_y_64week}


            stats_4week.text = area+'(last 4 weeks mae):\n'
            stats_64week.text = area+'(last one year mae):\n'
            mae_source_4week.data={
                'model':   [ model for model in models if model!='truth'],
                'mae':[ pred_4week_mae['{}_{}'.format(area,model)] for model in models if model!='truth'],
            }
            mae_source_64week.data={
                'model':   [ model for model in models if model!='truth'],
                'mae':[ pred_64week_mae['{}_{}'.format(area,model)] for model in models if model!='truth'],
            }

    geo_source.on_change('selected',my_tap_handler)

    layouts = column(fig_predict,stats_4week,data_table_4week)
    layouts=row(p,layouts)
    layouts = column(layouts,fig_predict_1year,select,stats_64week,data_table_64week)
    
    return layouts



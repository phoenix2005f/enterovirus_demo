
# coding: utf-8

# In[1]:


from bokeh.io import curdoc
from bokeh.layouts import column,row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import layout
import pandas as pd
import numpy as np
from bokeh.models import BoxAnnotation
from random import randint
import json

from bokeh.io import show, output_notebook, output_file
from bokeh.models import (
    GeoJSONDataSource,
    HoverTool,
    LinearColorMapper,
    CategoricalColorMapper,
    Button
)

from bokeh.palettes import Viridis6
from bokeh.models.widgets import Tabs, Panel

from area_predict import output_res


# In[2]:


areas = ['南區','北區','東區','高屏區','台北區','中區']
# areas = output_res()
tools = 'pan,wheel_zoom,xbox_select,reset'
color_list=['black','red','blue','green','cyan','yellow']
observe_list = ['腸病毒總人數','區週平均溫度','平均RH']
area_dict = {}


hist_dict = {}
source_history = ColumnDataSource(data={'x':[],'腸病毒總人數':[],'區週平均溫度':[],'平均RH':[]})


hist_fig_dict={}
for observe in observe_list:
    hist_fig_dict[observe] = figure(plot_width=1000, plot_height=350, tools=tools, x_axis_type='datetime', active_drag="xbox_select")





# In[3]:


for idx,area in enumerate(areas):
    area_dict[area]={}
    hist_dict[area]={}
    
    area_dict[area]['df'] = pd.read_csv('./data/{}.csv'.format(area))
    temp_df = area_dict[area]['df']
    
    total_people = temp_df['腸病毒總人數'].values
    area_dict[area]['total_people'] = total_people
    area_dict[area]['DT'] = pd.to_datetime(temp_df['DT'].values)
    area_dict[area]['mva'] = temp_df['腸病毒總人數_moving_avg'].fillna(0).values
    area_dict[area]['explode'] = temp_df['爆發預測'].fillna(0).values
    area_dict[area]['figure'] = figure(plot_width=500, plot_height=120, tools=tools, x_axis_type='datetime',y_range=(0,max(total_people)+20 ), active_drag="xbox_select") 
    area_dict[area]['figure'].xaxis.axis_label = '日期'
    area_dict[area]['figure'].yaxis.axis_label = '腸病毒人數'
    area_dict[area]['figure'].toolbar.logo = None
    area_dict[area]['figure'].toolbar_location = None
    
    area_dict[area]['figure'].title.text = area
    area_dict[area]['src'] = ColumnDataSource(dict(x=[],y=[],move_avg=[],alpha=[]))
    
    hist_dict[area]['src'] = ColumnDataSource(data={'x':pd.to_datetime(temp_df['DT'].values),'腸病毒總人數':total_people,'區週平均溫度':temp_df['區週平均溫度'].values,'平均RH':temp_df['平均RH'].values})

    
    


# In[ ]:


callback_id = None
def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(update, 1000)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)
button = Button(label='❚❚ Pause', width=60)
button.on_click(animate)


# In[ ]:





# In[4]:


with open('./twgeo_easy_rates.json', 'r') as file:
    json_str = file.read()
    geo_source = GeoJSONDataSource(geojson=json_str)
    twgeo_json = json.loads(json_str)
    

color_mapper = LinearColorMapper(palette=["blue", "red"],high=1,low=0)

TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"

p = figure(title="Taiwan", tools=TOOLS, x_axis_location=None, y_axis_location=None, width=600, height=800)
p.background_fill_color = 'beige'
p.border_fill_color = 'black'
p.border_fill_alpha = 0.05
p.grid.grid_line_color = None
p.toolbar.logo = None
p.toolbar_location = None

for i in range(22):
    if twgeo_json['features'][i]['properties']['explode']==0:
        twgeo_json['features'][i]['properties']['line_width'] = 0.5
    else:
        twgeo_json['features'][i]['properties']['line_width'] = 4

geo_source.geojson = json.dumps(twgeo_json)

figure_patch = p.patches('xs', 'ys', fill_alpha=0.7,fill_color={'field':'explode','transform':color_mapper},line_color='black', line_width='line_width',source=geo_source)



hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [("name", "@name"),("index","$index"),("(Lon,Lat)", "($x, $y)")]






# In[5]:


for idx,area in enumerate(areas):
    source = area_dict[area]['src']
    source_history = hist_dict[area]['src']
    
    area_dict[area]['figure'].line(x='x',y='y',color='blue',source=source)
    area_dict[area]['figure'].line(x='x',y='move_avg',color='green',source=source)
    area_dict[area]['figure'].segment(x0='x', y0='move_avg', x1='x', y1=0, line_width=45, color='red',line_alpha='alpha', source=source)  
    
    
    for observe in observe_list:
        hist_fig_dict[observe].line(x='x', y=observe, source = source_history,color=color_list[idx],legend=area,muted_color=color_list[idx])
        
        
for observe in observe_list:
    
    hist_fig_dict[observe].legend.location = "top_left"
    hist_fig_dict[observe].legend.click_policy = "hide"
    hist_fig_dict[observe].xaxis.axis_label = 'Date'
    hist_fig_dict[observe].yaxis.axis_label = observe
    hist_fig_dict[observe].toolbar.logo = None
    hist_fig_dict[observe].toolbar_location = None
    


# In[10]:



mva = 0
ct=0

def update():
    global ct,mva

    for area in areas:
        temp_explodes = area_dict[area]['explode']
        temp_explode = temp_explodes[ct]
        
        
        for i in range(22):
            if twgeo_json['features'][i]['properties']['area']==area:
                twgeo_json['features'][i]['properties']['explode']=temp_explode
                if temp_explode==0:
                    twgeo_json['features'][i]['properties']['line_width']=0.5
                else:
                    twgeo_json['features'][i]['properties']['line_width']=4
                
        moving_avg = area_dict[area]['mva']
        dt = area_dict[area]['DT']
        total = area_dict[area]['total_people']
        alpha = 0 if temp_explode == 0 else 0.2
    
        new_data = dict( x=[dt[ct]],y= [total[ct]],move_avg = [moving_avg[ct]],alpha=[alpha] )
        area_dict[area]['src'].stream(new_data,rollover=20)
        
        p.title.text = 'Taiwan {}'.format( str(dt[ct])[:-8] )
    geo_source.geojson = json.dumps(twgeo_json)
    
   #     p.patches('xs', 'ys', fill_alpha=0.7,fill_color={'field':'explode','transform':color_mapper},line_color='black', line_width=0.5,source=geo_source) 
    
    ct+=1
#     print(source.data)




layouts = column([area_dict[area]['figure'] for area in areas ]+[button])
layouts = row(layouts,p)

# layouts = column(layouts,column([hist_fig_dict[observe] for observe in observe_list]))
layouts_b = column([hist_fig_dict[observe] for observe in observe_list])
layouts_c = output_res()


tabs = Tabs(tabs=[
        Panel(title="realtime_demo", child = layouts),
        Panel(title="predictions", child = layouts_c),
        Panel(title="history data",child = layouts_b)
    ])
curdoc().add_root(tabs)
callback_id = curdoc().add_periodic_callback(update,1000)




# In[122]:


# geo_source.geojson


# In[ ]:





# In[ ]:





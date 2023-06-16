#!/usr/bin/python3  # REMOVE FOR pythonanywhere

dir1 = "App3/"; dir2 = "NZ_maps/"; dir3 = "static/images/" # LOCAL
#dir1 = "/home/steviecurran/mysite/App3/"; dir2 = "/home/steviecurran/NZ_maps/"; dir3 = "/home/steviecurran/mysite/static/images/"  # pythonanywhere

import numpy as np
import pandas as pd
import os 
import sys
import calendar
import datetime as dt
from datetime import date, timedelta, datetime
from shutil import get_terminal_size
pd.set_option('display.width', get_terminal_size()[0]) 
pd.set_option('display.max_columns', None)
import warnings
warnings.filterwarnings("ignore")

import dash
from dash import Dash, html, dcc, Input, Output, ctx, State
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions=True 

df = pd.read_csv(dir1+"greenhouse-gas-emissions-by-region-industry-and-household-year-ended-2021-csv.csv"); #print(df)
df = df.rename(columns = {'gas':'Gas'}); #print(df)

#### CHECK POPULATION OF UNIQUE VALUES IN A GIVEN FIELD #####
def val_counts(data,para):
    cols = data[para].unique()
    for (i,col) in enumerate(cols):
        temp = data[data[para] == col]
        print("For %s = %s there are %d values" %(para,col,temp[para].count()))

#val_counts(df,'anzsic_descriptor')
#val_counts(df,'anzsic_descriptor2') # MORE GENERIC CLASSES
#val_counts(df,'category') # NOT ALL Total there are 6135 values
#val_counts(df,'units') # ALL Kilotonnes there are 6900 values
# SO MORE STRAIGHTFORWARD THAN greenhouse-gas-emissions-industry-and-household-year-ended-2021.csv
#val_counts(df,'magnitude') # ALL Carbon dioxide equivalents there are 6900 values
# SO NO REAL PRE-POCESSING REQUIRED, UNLIKE DATA ABOVE. ALO HAVE YEAR AND REGION HERE 
#val_counts(df,'region')
###### PER CAPITA.  FROM Stats NZ ##################
df_pop = pd.read_csv(dir1+'estimated-resident-population-of-new-zealand_-at-31-march-2023.csv')
#print(df_pop) ## Mar-91 TO Mar-23 IN 3 MONTH INCREMENTS
df_pop[['month','year']] = df_pop['As at'].str.split('-', expand = True)
df_pop = df_pop[df_pop['month'] == "Dec"]
del df_pop['As at']; del  df_pop['month']
df_pop['year'] = df_pop['year'].astype(int)
df_pop.loc[df_pop['year'] >= 91, 'year'] = 1900 + df_pop['year']
df_pop.loc[df_pop['year'] <= 91, 'year'] = 2000 + df_pop['year']
#print(df_pop) # CAN NOW MERGE

df1 = pd.merge(df, df_pop, on = ['year'], how = 'inner');
df1['tpc'] = 1000*df1['data_val']/df1['Estimated resident population'] # TONNES PER CAPITA

########### TIDYING UP ###############
del df1['units']; del df1['magnitude'] # ALL Kilotonnes  Carbon dioxide equivalents
df1['Mtonnes'] = df1['data_val']/1000
del df1['data_val']
dates = df1['year'].unique(); #print(dates)
dates1 = dates[ : -1]
dates2 = dates[1:]
#print(df1)

########### DOUBBLE DIPPING - PUBLISHED VALUE FOR 2020 IS 79.8 ###############
#df2 = df1.copy()
df2 = df1[df1['anzsic_descriptor'] != "Primary industries"] # DOUBLE DIPPING?
df3 = df2[df2['anzsic_descriptor'] != "Agriculture"] 
df1 = df3[df3['anzsic_descriptor'] != "Manufacturing and construction"] 
df2  = df1[df1['anzsic_descriptor'] != "Forestry and logging, fishing, and agricultural support services"]

############ SEPARATING OUT TOTALS #####################
## NOT THE SAME TOTALS AS IN PREVIOUS CSV!!!
temp  = df2[df2['anzsic_descriptor'] == "Total"]; #print(totals)
#totals = temp[temp['Gas'] != 'Carbon dioxide'] # DOUBLE DIPPING? IN Carbon dioxide equivalents?
totals = temp[temp['Gas'] != 'Carbon dioxide equivalents'] #
total_inds = df2[df2['anzsic_descriptor'] == "Total all industries"] # HAS THE DIFFERENT GASES
temp = df2[df2['anzsic_descriptor'] != "Total"];# print(temp)
not_totals = temp[temp['anzsic_descriptor'] != "Total all industries"]

#val_counts(not_totals,'anzsic_descriptor') # CHECK
############# SECTORS - FOR RADIO BUTTONS IN SIDEBAR ##############
sectors = sorted(not_totals['anzsic_descriptor'].unique());
sectors.insert(0, "All") # WANT AT START

print(sectors)
#############################################################
slider_marks = {}  # SLIDER USES A DICTIONARY
for i in range(1,11):
    slider_marks[i] = "%s" %(i)

font = 16 # DEFAULT FONT SIZE    

###################################### DASHBOARD #####################
SIDEBAR_STYLE1 = {"position": "fixed", "top": 0,"left": 0,"bottom": 300,"width": "20rem",
                 "padding": "2rem 1rem","background-color": "#4C4E52",  "color": "white"}
SIDEBAR_STYLE2 = {"position": "fixed","top": 300,"left": 0,"bottom": 0,"width": "20rem",
                 "padding": "2rem 1rem","background-color": "#4C4E52",  "color": "white"}
CONTENT_STYLE = {"margin-left": "20rem", "margin-right": "0rem", "padding": "2rem 1rem"}

sidebar1 = html.Div([
    html.Div(  
        dbc.Row([
            html.Div(className='three columns', children=[
                html.P("Start year"),
            dcc.Dropdown(
                dates1,df1['year'].iat[0],
                id='drop1',
                style={'color': 'black','font-weight':'bold','fontSize': 14},
            ),
                ],style=dict(width='40%'),
                     ),
            html.Div(className='three columns', children=[
                 html.P("End year"),
            dcc.Dropdown(
                dates, df1['year'].iat[-1],
                id='drop2',
                style={'color': 'black','font-weight':'bold','fontSize': 14},
                ),
                ],style=dict(width='40%'),
                     ),
            
    html.Div(className='three columns', children=[
        html.P("All"),
                
        dcc.Checklist(
            [''], 
            id='check-all',
            inline=True
        ),
            ], style=dict(width='10%'),
             ),
            # Make sure that you're actually serving the image:
            dbc.CardImg(src =dir3+"png-transparent-new-zealand-aotearoa-map-travel-destination-north-island-south-island.png",
                        style={'width':'180px','height':'180px','margin-left': '50px','margin-top': '10px'}),
            
            html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
            html.P("Emission sector", style={'margin-left':'2px','margin-top':'120px'}),
            ]
                ),
    ),
  ], style=dict(SIDEBAR_STYLE1),
                   )  

sidebar2 = html.Div([
    html.Div([
        dcc.RadioItems(
            sectors,
            'All', # default
            id='sector-radio',
            #inline=False,
            inputStyle={"margin-right": "10px","margin-left": "0px","margin-top": "5px"}
        ),
    ],#style=dict(display='flex', justifyContent='left'),
             ),
], style=dict(SIDEBAR_STYLE2,overflow= "scroll"),# TRYING TO FORCE NEW LINE PER BUTTON
                   )

content = html.Div([
    html.P("New Zealand Greenhouse Gas Emissions",
           style={'font-family':'Arial Black','color': 'black',
                  'fontSize': 24,'textAlign':'center'}),
    dbc.Row(children =[
        dbc.Col([
            dbc.CardBody([
                dbc.CardImg(src = dir3+"Flag_of_New_Zealand.svg.png",
                            style={'width':'200px','margin-left': '25px','margin-top': '25px'}),
                #html.P("CO<sub>2</sub>", id='text-out',
                html.Div(id='text-out', style={'color': 'white','margin-left':'30px','color':
                                               'white','fontSize': 18,'font-weight':'bold',
                                               'margin-top':'20px','margin-right':'20px'}),
                html.Div(id='text-out_1', style={'color': 'white','margin-left':'30px','color':
                                               'white','fontSize': 16,'font-weight':'bold',
                                               'margin-top':'10px','margin-right':'20px'}),
                html.Div(id='text-out_1a', style={'color': 'white','margin-left':'30px','color':
                                               'white','fontSize': 16,'font-weight':'bold',
                                               'margin-top':'10px','margin-right':'20px'}),
                html.Div(id='text-out_1b', style={'color': 'white','margin-left':'30px','color':
                                               'white','fontSize': 16,'font-weight':'bold',
                                               'margin-top':'10px','margin-right':'20px'}),
                html.Div(id='text-out_1c', style={'color': 'white','margin-left':'30px','color':
                                               'white','fontSize': 16,'font-weight':'bold',
                                               'margin-top':'10px','margin-right':'20px'}),
        
            ],style={"width": "250px","height": "380px",'margin-top':'10px','background-color': '#101D42','margin-right':'0px',},
                         ),
        ],style={'width': "240px"},
                ),
   

        dbc.Col([
            html.P("Emissions by sector [Megatonnes]", style={'margin-left': '0px','margin-top':'0px',
                                                 'margin-bottom':'0px','font-weight':'bold','fontSize': 18}),
            dcc.Graph(id='donut1', style={'margin-left': '0px'}),

            
           html.Div([
                "Maximum % to show [other sectors]", #,style={"width": "240px"), 
            dcc.Slider(
                0.1,5,0.1,
                id='slider',
                marks=slider_marks,
                value=1
                ),
                ], style={'width': "280px",'margin-left': '320px'},
               ),
            ], style={'margin-left':'20px','margin-top':'0px','margin-bottom':'0px'},
        ),
         ], style={'width':'95%','padding': '0px','margin-left':'0px','margin-top':'0px','margin-bottom':'0px'},
           ),
    
          html.Br(),html.Br(),html.Br(),
    
    dbc.Row(children =[
        dbc.Col([
        html.Div(id='text-out2',style={'fontSize': 18,'font-weight':'bold','margin-top': '0px',
                                       'margin-left': '20px'}), 
        dcc.Graph(id='bar1', style = {'height':450, 'width':'40%','margin-right': '0px',
                                      'margin-left': '0px','margin-top': '0px'}),
            ]),
        dcc.Graph(id='map1', style = {'height':600, 'width':'55%',
                                      'margin-left': '-10px', 'margin-right': '0px', 'margin-top': '-60px'}),
    ],
    ),
     html.Br(),html.Br(),html.Br(),

dbc.Row(children = [
        dbc.Col([
        "Emissions over time by gas species",
        ], style={'margin-left': '0px','margin-top':'0px','font-weight':'bold','fontSize': 18},
                ),
        dcc.Dropdown(
            ["Megatonnes", "Tonnes per capita"],
            "Megatonnes", # DEFAULT
            id='gt-drop',
            style={'width': '45%', 'margin-left': '20px', 'margin-right': '-40px', 'font-weight':'bold','fontSize': 14},
        ),
        dcc.Checklist(
            ['Show total'], 
            id='check-total',
            inputStyle={'margin-left': '0px', 'margin-right': '10px'}
        ),
    ], style={'margin-left': '0px', 'margin-right': '0px', 'font-weight':'bold','fontSize': 16},
            ),
    
    dcc.Graph(id='gas-total'),
     
    

  ],style=CONTENT_STYLE, id="page-content",
                   )

###########################################################################################
app.layout = html.Div([ dcc.Location(id="url"), sidebar1, sidebar2,content ])

@app.callback(
    Output('donut1', 'figure'),
    Output('gas-total', 'figure'),
    Output('text-out', 'children'), Output('text-out_1', 'children'), Output('text-out_1a', 'children'),
    Output('text-out_1b', 'children'), Output('text-out_1c', 'children'),Output('text-out2', 'children'),
    Output('map1', 'figure'),Output('bar1', 'figure'), # SAME ORDER AS ABOVE
    Input('check-all', 'value'),
    Input('drop1', 'value'), Input('drop2', 'value'),
    Input('slider', 'value'),
    Input('sector-radio', 'value'),
    Input('gt-drop', 'value'), # pc
    Input('check-total', 'value') 
    )

def donut_etc(check,date1,date2,slide_value,sector_radio,pc,g_total):

    gas_totals = totals.groupby(['Gas','year'])['Mtonnes'].sum().reset_index(); 
    #print(gas_totals)
    
    if check == None or check == []:  
        if date1 < date2:
            t = not_totals[not_totals['year'] >=  date1]
            dff = t[t['year'] <=  date2]
            g = gas_totals[gas_totals['year'] >=  date1]
            gas_years = g[g['year'] <=  date2]
           
        else:  # MAKING REVERSABLE
            t= not_totals[not_totals['year'] >=  date2]
            dff = t[t['year'] <=  date1]
            g = gas_totals[gas_totals['year'] >=  date2]
            gas_years = g[g['year'] <=  date1]
            
    else:
        dff = not_totals.copy()
        gas_years = gas_totals.copy()
        date1 = df['year'].iat[0]; 
        date2= df['year'].iat[-1];

    ind_totals = dff.groupby(['anzsic_descriptor'])['Mtonnes'].sum().reset_index(); #print(ind_totals)
    ind_totals['perc'] = 100*ind_totals['Mtonnes']/ind_totals['Mtonnes'].sum()
    total_ind_total = ind_totals['Mtonnes'].sum()
    
     
    cut = slide_value # CUT-OFF FOR others BIN IN PERCENT - PUT AS SLIDER?
    ind_totals.loc[ind_totals['perc'] < cut, 'anzsic_descriptor'] = "Other sectors [< %1.1f%% each]" %(cut)
    #print("\n%d - %d\n..." %(date1,date2), ind_totals)
    
    donut = go.Figure(data=[go.Pie(labels= ind_totals['anzsic_descriptor'].str.slice(0,28),
                                   values=round(ind_totals['Mtonnes'],0), hole=.4)])
    donut.update_traces(hoverinfo='label+percent', textinfo='value', #percent',
                        textfont_size=14, marker=dict(line=dict(color='#000000', width=2)))
    
    donut.update_layout(width=600, height=350,margin={"pad": 0, "t": 20,"r": 0,"l": 0,"b": 0})
    ## width AND height ARE SPACED RESERVED SO height < width OTHERWISE WHITESPACE
    donut.update_layout(legend=dict(yanchor="top",y=0.95,xanchor="right", x=1.8)) ### BIGGER FONT???
    ############### MAP - CAN'T FIND DIRECT GREENHOUSE MAP ###########
    import geopandas as gpd 
    import pyproj

    fp = dir2+"nz-police-district-boundaries-29-april-2021.shx"
    gdf = gpd.read_file(fp)
    gdf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    del gdf['D_MACRON']
    gdf['DISTRICT_N'] = gdf['DISTRICT_N'].replace({'Auckland City': 'Auckland'})
    gdf = gdf.rename(columns = {'DISTRICT_N':'region'}); #print(gdf)
    dfm1 = totals.copy();  # GIVES OPTION TO CHANGE
    dfm1['region'] = dfm1['region'].replace({'Tasman/Nelson': 'Tasman'})
    dfm1['region'] = dfm1['region'].replace({'Nelson': 'Tasman'})
    dfm1['region'] = dfm1['region'].replace({'Marlborough': 'Tasman'}) # TRIPLE COUNTING
    dfm1['region'] = dfm1['region'].replace({"Hawke's Bay": 'Eastern'}) 
    dfm1['region'] = dfm1['region'].replace({'Gisborne': 'Eastern'}) # DOUBLE COUNTING
    dfm1['region'] = dfm1['region'].replace({'Manawatu-Whanganui': 'Central'})
    dfm1['region'] = dfm1['region'].replace({'Taranaki': 'Central'}) # DOUBLE COUNTING
    dfm1['region'] = dfm1['region'].replace({'Otago': 'Southern'})
    dfm1['region'] = dfm1['region'].replace({'Southland': 'Southern'})
    dfm1['region'] = dfm1['region'].replace({'West Coast': 'Southern'}) # TRIPLE COUNTING
    #print(dfm1)
    if check == None or check == []:  
        if date1 < date2:
            t = dfm1[dfm1['year'] >=  date1]
            dfy = t[t['year'] <=  date2]
        else:  # MAKING REVERSABLE
            t= dfm1[dfm1['year'] >=  date2]
            dfy = t[t['year'] <=  date1]   
    else:
        dfy = dfy.copy()
        date1 = df['year'].iat[0]; 
        date2= df['year'].iat[-1];

    temp = dfy.groupby(['region'])['Mtonnes'].sum().reset_index() # NEED TO PRESERVE TITLES
    auk1 = "Aukland [Counties/Manukau]"; auk2 = "Aukland [Waitemata]"  ## AUCKLAND SUBURBS
    #temp2 = temp[temp['region'] == "Auckland"]; #print(auk_sub)
    auk_sub = 0 # float(temp2['Megatonnes CO2 equivalent']); # SO NOT COUNTING MORE THAN ONCE
    new_row = {'region':'Counties/Manukau', 'Mtonnes': auk_sub}
    temp = temp.append(new_row, ignore_index = True); #print(temp)
    new_row = {'region':'Waitemata', 'Mtonnes': auk_sub}
    temp = temp.append(new_row, ignore_index = True); #print(temp)
    df = pd.merge(temp, gdf, left_on=['region'], right_on = ['region'])
    df['region'] = df['region'].replace({'Counties/Manukau':auk1})
    df['region'] = df['region'].replace({'Waitemata':auk2}); #print(df)

    temp1 = df[df['region'] != auk1]; 
    temp2 = temp1[temp1['region'] != auk2]; 
    total_em = round(temp2['Mtonnes'].sum(),1); #print(total_em) 

    df = df.set_geometry("geometry").set_index("region")

    map1 = px.choropleth(df, geojson=df.geometry,locations=df.index,
                         color="Mtonnes",height=600,color_continuous_scale="rainbow");
    map1.update_geos(fitbounds="locations", visible=False) 
    map1.update_layout(margin={"pad": 0, "r":0,"t":0,"l":0,"b":0})
    map1.update_layout(coloraxis_colorbar=dict(thicknessmode="pixels",
                    thickness=20, lenmode="pixels",xanchor="left", x = 0.8,
                            len=300,title_side = 'right',tickfont_size=14

    ))
    
    ##############
 
    if pc== "Megatonnes":
        para = 'Mtonnes'
        ylabel = "CO<sub>2</sub> equivalent [Megatonnes]"
    else:
        para = 'tpc' # Kilotonnnes per capita
        ylabel = "CO<sub>2</sub> equivalent tonnes/capita"
  
    gas_totals = totals.groupby(['year','Gas'])[para].sum().reset_index(); #print("Gas totals ...\n",gas_totals)
    total_totals = totals.groupby(['year'])[para].sum().reset_index()
              
    y = gas_totals[para]
        
    gt = px.line(gas_totals, x="year", y=y, color='Gas')
    if g_total != None and g_total != []:
        gt.add_trace(go.Scatter(x=total_totals['year'], y=(total_totals[para]),
                                name = "Total",
                                line=dict(width=2,color="black")))
          
    gt.update_traces(line=dict(width=2.5))
    gt.update_xaxes(showgrid=False, linecolor = "black", linewidth = 3,mirror = True,title="Year",
                    title_font=dict(size=font),tickfont=dict(size=font))
    gt.update_yaxes(showgrid=False, linecolor = "black", linewidth = 3,mirror = True, title=ylabel,
                    title_font=dict(size=font),tickfont=dict(size=font))
    gt.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                     width=900, height=350,margin={'l': 40, 'b': 40, 't': 20, 'r': 20},
                     font=dict(size=font), hovermode='closest')

    if  sector_radio == 'All':
        dfs = dff.groupby(['region'])['Mtonnes'].sum().reset_index()
        ymax = dfs['Mtonnes'].max(); 
            
    else:
        dfs = dff[dff['anzsic_descriptor'] == sector_radio]
        val =dfs.groupby(['region'])['Mtonnes'].sum()
        ymax = val.max()

    
    temp = sector_radio.split(" "); s_rad = temp[0]; #print(s_rad) # SOME STRING TOO LONG FOR PLOT
    if len(temp) > 1:
        label_text = "%s..." %(s_rad)
    else:
        label_text = s_rad

    bar = px.histogram(x=dfs['region'], y=dfs['Mtonnes'])
    
    bar.update_traces(marker_color='rgb(160,160,160)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=3, opacity=1)
    
    bar.update_xaxes(showgrid=False, linecolor = "black", linewidth = 3,mirror = True, tickangle = 90,
                     title="",title_font=dict(size=font),tickfont=dict(size=font),
                     categoryorder="total descending")

    bar.update_yaxes(showgrid=False, linecolor = "black", linewidth = 3,mirror = True, 
                     title="CO<sub>2</sub> equivalent by region  [Megatonnes]",
                     title_font=dict(size=font),tickfont=dict(size=font),
                     title_standoff = 40) # SPACE BETWEEN LABLE AND TICKS

    bar.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                     width=450, height=550,margin={"pad": 0,'l': 0, 'b': 0, 't': 40, 'r': 0},
                     font=dict(size=16), hovermode='closest',  bargap=0)
      
    bar.add_annotation(font=dict(color='black',size=font), x=11.5, y=0.98*ymax ,showarrow=False,text="%s, %s to %s" %(label_text,date1,date2))

    total_ind = ind_totals[ind_totals['anzsic_descriptor'] == "Agriculture"]; total_Mt = total_ind['Mtonnes']
    
    #bar.add_annotation(font=dict(color='black',size=font), x=11.5, y=0.88*ymax ,showarrow=False,text="Total = %1.2f [%1.1f%%]" %(total_Mt,total_Mt))


    gas_years_total = gas_years['Mtonnes'].sum()
    
    CO2 = gas_years[gas_years['Gas'] == "Carbon dioxide"]; CO2_tot = CO2['Mtonnes'].sum(); #print(CO2_tot)
    CO2_TOT = CO2_tot # + CO2e_tot
    #CO2_text = r"$CO_2$" # "CO<sub>2</sub>"
    #CO2_text = r"$CO_{2} %1.0f$" %(CO2_TOT)
    
    N2O = gas_years[gas_years['Gas'] == "Nitrous oxide"]; N2O_TOT = N2O['Mtonnes'].sum(); 
    CH4 = gas_years[gas_years['Gas'] == "Methane"]; CH4_TOT = CH4['Mtonnes'].sum()
    FG =  gas_years[gas_years['Gas'] == "Fluorinated gases"]; FG_TOT = FG['Mtonnes'].sum(); #print(FG_TOT)
  
    return donut,gt,'Over %s to %s: %1.1f Megatonnes' %(date1,date2,gas_years_total), "CO2 = %1.1f" %(CO2_TOT),"CH4 = %1.1f" %(CH4_TOT), "N2O  = %1.1f" %(N2O_TOT), "Fluorinated gases = %1.1f " %(FG_TOT), 'Sector by region over %s to %s' %(date1,date2),map1,bar

      

if __name__ == '__main__':
    #app.run()  # pythonanywhere
    #app.run_server(debug=True) # http://Stevies-Air.staff.vuw.ac.nz:8050/ VUW
    #app.run_server(host = '172.20.10.3',debug=True) # http://172.20.10.3:8050/   PHONE
    app.run_server(host = '192.168.178.55',debug=True) #  http://Stevies-Air.fritz.box:8050/   HOME


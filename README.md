# NZ-greenhouse
New Zealand Greenhouse Gas Emissions Dashboard

From StatsNZ I downloaded the three available Greenhouse Gas Emissions datasets, finding “Greenhouse gas emissions by region, industry and household: Year ended 2021 – CSV” to be the most comprehensive, containing data on each of the main greenhouse gases by sector and regions over 2007 to 2021
(although some cleaning was required, as this contained overlapping sectors and CO2 and CO2 equivalents leading to multiple counts).

Again, using Python Dash, I built the dashboard, from which it is seen that “agriculture, forestry and fishing” is New Zealand's largest greenhouse emission sector (with agriculture being by far the most dominant).

Also, the Waikato and Canterbury, where agriculture is primarily based, are the highest emitting regions.  Lastly, by combining the data with population numbers, it is seen that there has been a decrease in emissions per capita over this period. However, the total amount remains roughly constant.

The dashboad is currently acessible at http://steviecurran.pythonanywhere.com

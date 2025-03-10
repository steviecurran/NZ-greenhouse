# New Zealand Greenhouse Gas Emissions dashboard

From StatsNZ I downloaded the three available Greenhouse Gas Emissions datasets, finding “Greenhouse gas emissions by region, industry and household: Year ended 2021 – CSV” to be the most comprehensive, containing data on each of the main greenhouse gases by sector and regions over 2007 to 2021
(although some cleaning was required, as this contained overlapping sectors and CO<sub>2</sub> and CO<sub>2</sub> equivalents leading to multiple counts).

Again, using Python Dash, I built the dashboard, from which it is seen that “agriculture, forestry and fishing” is New Zealand's largest greenhouse emission sector (with agriculture being by far the most dominant).

Also, the Waikato and Auckland are the highest emitting regions overall. Lastly, by combining the data with population numbers, it is seen that there has been a decrease in emissions per capita over this period. However, the total amount remains roughly constant.

![](https://raw.githubusercontent.com/steviecurran/NZ-greenhouse/refs/heads/main/screen.png)



# Meteorite Category

## Questions Addressed
1. **How many** meteorites of each category have landed over the years?
2. **What proportion** of meteorites of each category have landed over the years?
3. What is the **relationship** between the amount/ proportion of meteorite landings by category and
   1. geographical distribution of meteorite landings
   2. year of meteorite landing/ discovery
   3. meteorite mass

## Visualisations: Bar Graph and Pie Chart

Since meteorite category is a discrete measure related here to questions of *how many* and 
*what proportion*, the classic bar and pie chart visualisations are appropriate. The option to coordinate
map markers to the colour of the bar/ segment meteorite category (as described in the design rationale for
the [scatter map plot](/part_1/visualisation%20design/scatter_plot_map.md)), and the ability to make points corresponding to certain
categories appear/ disappear simultaneously on the map and bar chart by selecting/ deselecting legend
items addresses question 3i, while the range sliders in the control box help address questions 3ii and iii.

**Bar graph:**
![](/part_1/visualisation%20design/images/bar%20graph.png)

**Bar chart hover functionality:**
![](/part_1/visualisation%20design/images/bar%20chart%20hover.png)

**Pie chart:**
![](/part_1/visualisation%20design/images/pie%20chart.png)

**colour palette:**
![](/part_1/visualisation%20design/images/category%20colour%20palette.png)


## Explanation

It is commonplace to colour-code discrete categorical data using diverging colour palettes (Indeed Editorial Team, 2022). The colour palette (displayed above) was chosen accordingly.
Semantic associations were also considered (iron was assigned to red, stony to blue, grey to uncategorised and overall,
earthy tones were used) to improve the intuitiveness of the visualisation. This is particularly important considering that 
the need to look between one end of the screen and the other in order to compare the bar/ pie chart to the colour-coordinated
map means that it is not convenient to be constantly referring to the legend too, and meaningful colour assignments tend to improve
information recall (Indeed Editorial Team, 2022).

There was a trade-off to consider between pie charts and bar charts for visualising meteorite category; pie charts tend to be more intuitive, especially 
regarding the question related to *proportion,* but bar charts are more informative in terms of communicating actual numerical values and answering the
*how many* question. It was eventually decided that the bar chart would be the main visualisation, with an option for the user to switch to viewing the data 
as a pie chart in order to get a feel for how two of the core charts referenced on the syllabus can represent the same data, and allow the more intuitive pie
chart to act as a point of reference when interpreting the bar chart.

## Evaluation

The fact that the category labels appear on the graphs as well as the legend offer improved convenience and reduce eyespan
to the sections of the visualisation concerning the data itself (Few, 2005). The decision to exclude gridlines from the bar chart was
made in the interest of reducing visual clutter or the "data-ink ratio," but it does risk alienating users more likely to
have been introduced to bar charts through manual construction on grid paper and textbook examples that would likely maintain
a grid structure to aid interpretation. Its absence here distances the chart from its construction slightly, which is not ideal
given the goal of educating users on the graphs themselves, despite the trade-off with visual minimalism. Furthermore, the absence
of the grid structure makes it challenging for the user to interpret the value directly from looking at the chart. The hover
functionality is a valuable inclusion which fortunately mitigates for this by allowing the user to read the numerical
value for each bar by hovering over it.

Another strength of these visualisations is the decision to include limited categories. Unwin et al. note that the "potential weakness"
in both bar and pie charts is most often the set of categories (Unwin et al., 2008). The original dataset contained over ten meteorite
categories which I put into broader categories during the data cleaning process. The original categorisation
would not have translated meaningfully into these chart forms as the number of labels needed would have created clutter and the number of bars
or segments would have resulted in a longer y-axis or smaller segments respectively which would have made comparison difficult.

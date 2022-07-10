# Visualisation Design

## Target Audience
The target audience is GCSE Maths students aged 15-16. This application is intended to
complement the Statistics component of GCSE Maths, which specifies the
following learning objectives (Department for Education, 2016, p. 11-12):
1. Interpret tables, charts and diagrams and know their appropriate use, including:
   1. frequency tables, bar charts and pie charts for categorical data,
   2. vertical line charts for ungrouped discrete numerical data
   3. tables and line graphs for time series data 
   4. interpret diagrams for grouped discrete data and continuous data, i.e. histograms
2. Interpret, analyse and compare the distributions of data sets from uni-variate empirical 
distributions through:
   1. appropriate graphical representation involving discrete, continuous and grouped data,
   including box plots
   2. appropriate measures of central tendency
3. Apply statistics to describe a population

With the goal of helping students gain an understanding of these core statistical concepts, the application takes the form of a 
dashboard that allows users to visualise NASA's Meteorite Landings dataset through various visualisations as 
referenced in the syllabus. The chosen dataset is ideal as it includes discrete, continuous and grouped data, 
giving students the opportunity to familiarise themselves with various data types.

The application targets ambitious students eager to learn and willing to explore the syllabus content in their own time.
The intended target audience also has a significant interest in meteorites, as the core idea is that giving students
the opportunity to apply the tools they have been taught in the classroom to learn about a topic of personal interest will
encourage further engagement and an improved understanding of the syllabus content. The application is open-source in the
interest of widening equal access to educational resources.

This is an online application intended for desktop use, as it is assumed that the target audience, given the age group,
is familiar with technology and has access to an internet connection and laptops or desktop computers, either personally or
through schools. Although it is safe to assume that using the application will be intuitive and overly detailed
guidance unnecessary given the target audience, it is important that the user-interface maintains a simple and clear structure, as the data visualisations
themselves are expected to be relatively unfamiliar to users. It is likely that being faced with a webpage containing many visualisations
at once and lacking a clear structure could be overwhelming.

## Data
The dashboard aims to teach students how to use various data visualisations to gain information about the [Meteorite Landings dataset](https://data.nasa.gov/Space-Science/Meteorite-Landings/gh4g-9sfh).
The visualisations were designed with the objective of addressing questions about the properties of meteorite landings and
the relationships between these properties. The meteorite properties are:
1. Location of meteorite landing
2. Discovery of meteorite (was it seen falling or discovered after landing)
3. Category of meteorite
4. Year of landing/ discovery
5. Mass of meteorite

The specific questions addressed by each visualisation are outlined in the design rationales, linked in the *Visualisations* section below.

## Design
Alberto Cairo describes a "fundamental clash" between an approach to data visualisation which emphasises functionality
and one which treats it as an artistic endeavor, emphasising aesthetics (Cairo, 2012, ch. 3). The approach taken for this project is more suited
to the first camp. This decision was taken considering the primary aim of the visualisations to educate and provide users unfamiliar with
standard data visualisation techniques with an appreciation for how various charts and graphs can convey information about the meteorite
landings. An over-emphasis on aesthetic trivialities could result in an overly flamboyant feel to the dashboard that would distract
from the data itself and overwhelm users. In addition to minimising clutter and confusion, the choice of a functional approach is particularly
relevant to Edward Tufte's criticisms of "chartjunk" as exposing an underlying belief "that numbers and details are boring, dull, and tedious,
requiring ornament to enliven" (Tufte, 1990, p. 34); it is important that users *see* the data speaking for itself if they are to gain an appreciation
for data visualisation as a worthwhile tool.

This functional approach to the dashboard design manifests in:
- a minimalist design which splits the screen and uses tabs to ensure that there are only two visualisations visible at once, reducing clutter and keeping each graph within eye span (an important consideration according to Stephen Few (Few, 2005))
- a light-coloured background made up of whites and greys
- a lack of grid lines on charts (in line with Tufte's advice on minimising the data-ink ratio (Tufte, 1990))
- employing hover functionality rather than grid labels to communicate data that is not immediately evident from the charts/ graphs

See screenshots of the overall dashboard layout below:

**page header and control box:**
![](/part_1/visualisation%20design/images/page%20header.png)

**visualisations:**
![](/part_1/visualisation%20design/images/full%20page.png)

### Interactivity

Interactive components allow users to manipulate the dataset and charts by choosing between various data filters and settings.
It is expected that these features encourage users to pay attention to how the charts respond, familiarising them with the
relationship between the data and the visualisations in line with the educational objective. The interactive component also aims
to promote genuine engagement with the dataset by encouraging users to "cross the great chasm between passive consumption and active
exploration" as referenced by Daniel Haight (Haight, 2020).

There are two elements to the dashboard's interactive components:
- **data filtering:** 
  - the control box at the top of the page allows the user to apply various filters to the dataset
  - box and lasso selection of data points on the map filters the dataset geographically
  - selecting/ deselecting meteorite categories on the bar chart legend filters the data points that appear
  on the bar graph and map by category
- **chart/ graph editing:**
  - bar chart/ pie chart options to visualise number/ proportion of meteorites in different categories
  - histogram/ box & whisker plot options to visualise meteorite mass distribution
  - log/ linear scale options for the x-axis of the histogram and box & whisker plot
  - option to coordinate map marker size to meteorite mass or color to meteorite category

### Individual Data Visualisations
The design rationale and evaluation of the visualisations for each property (as described above) is linked in a separate .md file below:
1. [Location of meteorite landings: scatter plot map](/part_1/visualisation%20design/scatter_plot_map.md)
2. [Meteorite landings by category: bar graph & pie chart](/part_1/visualisation%20design/category_graphs.md)
3. [Meteorite landings by year: line graph](/part_1/visualisation%20design/year_graph.md)
4. [Meteorite landings by mass: histogram & box and whisker plot](/part_1/visualisation%20design/mass_graphs.md)

## References

Cairo, A. (2012). *The Functional Art: An introduction to information graphics and visualisation*, New Riders.

Cairo, A. (2016). *The Truthful Art: Data, Charts, and Maps for Communication*, New Riders.

Department for Education. (2016), [GCSE Mathematics subject content and assessment objectives](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/254441/GCSE_mathematics_subject_content_and_assessment_objectives.pdf), *Gov UK* [online].

Indeed Editorial Team (2022), [Color Choices in Data Visualizations: Importance and How To](https://www.indeed.com/career-advice/career-development/how-to-choose-color-for-data-visualizations). *Career Development* [online].

Few, S. (2005). *[Show Me the Numbers](https://courses.washington.edu/info424/2007/readings/Show_Me_the_Numbers_v2.pdf)*, University of Washington [online].

Grover, V. (2021). [Role of Interactive Maps in Data Visualization](https://www.toolbox.com/marketing/content-marketing/articles/role-of-interactive-maps-in-data-visualization/), *Toolbox* [online].

Haight, D. (2020). [Towards Better Visualisations: Part II - How to be More Effective](https://www.darkhorseanalytics.com/blog/towards-better-visualizations-part-2), *Dark Horse Analytics* [online].

Setlur, V. and Stone, M.C. (2016) [A Linguistic Approach to Categorical Color Assignment for Data Visualization](https://ieeexplore.ieee.org/abstract/document/7192709), *IEEE Transactions on Visualization and Computer Graphics*, 22(1), pp. 698-707.

Tufte, E. (1990). *Envisioning Information*, Graphics Press: Michigan.

Unwin, A. et al. (2008). *Handbook of Data Visualisation*(https://haralick.org/DV/Handbook_of_Data_Visualization.pdf). CASE: Berlin.

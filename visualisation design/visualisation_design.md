# Visualisation Design

## Target Audience
The target audience is GCSE Maths students aged 15-16. This application is intended to
complement the Statistics component of GCSE Maths, which specifies the
following learning objectives (Department for Education, 2016):
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
The intended target audience also has at least a mild interest in meteorites, as the core idea is that giving students
the opportunity to apply the tools they have been taught in the classroom to learn about a topic of personal interest will
encourage further engagement and an improved understanding of the syllabus content. The application is open-source in the
interest of widening equal access to educational resources.

This is an online application intended for desktop use, as it is assumed that the target audience, given the age group,
is familiar with technology and has access to an internet connection and laptops or desktop computers, either personally or
through schools. Although it is safe to assume that using the application will be intuitive and overly detailed
guidance unnecessary given the target audience, it is important that the user-interface maintains a simple and clear structure, as the data visualisations
themselves are expected to be relatively unfamiliar to users. It is likely that being faced with a webpage containing many visualisations
at once and lacking a clear structure could be overwhelming.

## Questions to be Addressed
The dashboard aims to teach students how to use various data visualisations to gain information about the Meteorite Landings dataset.
The visualisations were therefore designed with the objective of addressing questions about the properties of meteorite landings and
the relationships between these properties. The meteorite properties are:
1. Location of meteorite landing
2. Discovery of meteorite (was it seen falling or discovered after landing)
3. Category of meteorite
4. Year of landing/ discovery
5. Mass of meteorite

The specific questions addressed by each visualisation are outlined in the design rationales, linked in the *Visualisations* section below.

## Design Approach

the priority is interactivity and giving users the ability to control data filters because we want students to feel involved in the process
of *creating* the visualisations. Truly engaged with the data because they're here first and foremost to learn about the visualisations, rather
than the meteorites

data filters, interactivity, control boxes, general visual appearance of the dashboard
UI should be intuitive and simple, not overwhelming (tab structure etc.)


## Visualisations
The design rationale of the visualisations for each property is linked in a separate .md file below:
1. [Location of meteorite landings: scatter plot map](https://github.com/ucl-comp0035/comp0034-cw1-i-serenaives/blob/master/visualisation%20design/scatter_plot_map.md)
2. [Meteorite landings by category: bar graph & pie chart](https://github.com/ucl-comp0035/comp0034-cw1-i-serenaives/blob/master/visualisation%20design/category_graphs.md)
3. [Meteorite landings by year: line graph](https://github.com/ucl-comp0035/comp0034-cw1-i-serenaives/blob/master/visualisation%20design/year_graph.md)
4. [Meteorite landings by mass: histogram & box and whisker plot](https://github.com/ucl-comp0035/comp0034-cw1-i-serenaives/blob/master/visualisation%20design/mass_graphs.md)

## References

Department for Education (2016), [GCSE Mathematics subject content and assessment objectives](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/254441/GCSE_mathematics_subject_content_and_assessment_objectives.pdf), Gov UK, p. 11-12
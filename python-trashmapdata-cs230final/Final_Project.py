'''
Name: Sky Pemberton
CS230: Section 5
Data: Trash Schedules by Address
URL:

Description:

This program is a tool that can be used to visually see when trash is being picked up in your mailing neighborhood,
zipcode, or district number. Users can select what neighborhood they are in, and see a map with all of the houses that
are located in the same neighborhood as you are. They can also see how big their neighborhood is compared to other
neighborhoods selected, and can see how many houses trash are being picked up on each day. For the next pages, users can
see what days their trash is being picked up by zip code using a bar chart, and by district number using a scatterplot.
'''

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import altair as alt
st.set_option('deprecation.showPyplotGlobalUse', False)

#reference for learning altair: https://www.youtube.com/watch?v=ms29ZPUKxbU, https://www.youtube.com/watch?v=_utVSETztbM


#load data function to read the data
def loaddata():
    return pd.read_csv("trashschedulesbyaddress_7000_sample.csv").set_index("sam_address_id")

#filter the data for the first page
def filter_data(sel_mn, sel_trashday):
    df = loaddata()
    df = df.loc[df["mailing_neighborhood"].isin(sel_mn)] #updates the dataframe with filtered rows where mailing neighborhood is present
    df = df.loc[df["trashday"].isin(sel_trashday)]
    return df

def all_mn(): #takes a list of all unique mailing neighborhoods in the dataframe, used for dropdown menu
    df = loaddata()
    lst = []
    for ind, row in df.iterrows(): #iterates over row
        if row['mailing_neighborhood'] not in lst: #checks if the value is in the list
            lst.append(row["mailing_neighborhood"]) #adds it to the list if not
    return lst
def count_mn(neighborhoods, df): #used to count the occurances of each neighborhood
    lst = [df.loc[df["mailing_neighborhood"].isin([mailing_neighborhood])].shape[0] for mailing_neighborhood in neighborhoods]
    # list comprehension that iterates through each neighborhood, and filters the DF based on whether the MN column matches the current neighborhood
    return lst

#count freq of trashday
def count_trashday(day, df):
    lst1 = [df.loc[df["trashday"].isin([trashday])].shape[0] for trashday in day]
    return lst1

#creating a list to show all of the days for the user input
def all_days():
    df = loaddata()
    lst = []
    for ind, row in df.iterrows():
        if row["trashday"] not in lst:
            lst.append(row["trashday"])
    return lst

#generating a bar chart based on the neighbordhood and day
def gen_bar_chart(mn, day):
    y = count_trashday(day, filter_data(mn, day))
    x = day
    plt.figure()
    plt.bar(x,y)
    plt.ylabel("# of Houses Collected that Day") #y axis label
    plt.xlabel("Day of the Week") #x axis label
    plt.title(f"# of Houses Collected for Selected Neighborhoods")
    return plt


#generating a pie chart based on relative amount of houses in selected data
def gen_pie_chart(counts, sel_mn):
    plt.figure()
    plt.pie(counts, labels=sel_mn, autopct="%.2f")
    plt.title(f"Relative Comparison of Amount of Houses in Each Neighborhood: {', '.join(sel_mn)}")
    return plt

#function that generates a map
def generate_map(mn, day):
    df = filter_data(mn, day)

    df.rename(columns={"x_coord":"lon", "y_coord": "lat"}, inplace= True)
    layer = pdk.Layer(type = 'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_radius=20,
                    get_color=[],
                    pickable=True
                  )
    view_state = pdk.ViewState(
                latitude=df["lat"].mean(),
                longitude=df["lon"].mean(),
                zoom=11,
                pitch=0)

    tool_tip = {"html": "Address:<br/> <b>{full_address}</b><br/>Trash Day: <b>{trashday}</b>",
            "style": { "backgroundColor": "black",
                        "color": "white"}
          }

    map = pdk.Deck(
                map_style='mapbox://styles/mapbox/outdoors-v11',
                initial_view_state=view_state,
                layers=layer,
                tooltip=tool_tip)
    st.pydeck_chart(map)

#title functions for my pages
def page1():
    st.title("Trash Schedule By Address")
def page2():
    st.title("Enter Zipcode to Find Collection Days")
def page3():
    st.title("District vs Collection Days")

#functions for second page

#takes dataframe and sel zipcode as input, filters df, and returns new df containing the rows
#with sel zipcode
def filter_zip(df, selected_zipcode):
    return df[df["zip_code"] == selected_zipcode]
    #compares values in zipcode column with the selected zipcode, and keeps only the rows that match the selected zipcode


#creating a bar chart using altair for both trashday and recollect day
def create_bar_chart(data, xcol, title):
    barchart = alt.Chart(data).mark_bar().encode( #creates bar chart in altair
        x=f'{xcol}:N', #specifies the x column as a categorical variable
        y='count():Q', #specifies the y column as a numeral variable
        tooltip=['count():Q'] #allows you to hover over chart to see
    ).properties(
        title=title #sets the title as the provided title
    )
    return barchart


def zipcode_page(): #creating the second page, adding the two charts
    st.sidebar.title("Filter Data by Zipcode")
    df = loaddata()
    sel_zipcode = st.sidebar.selectbox("Select Zip Code", df["zip_code"].unique()) #takes only the unique values and puts them in the box
    filtered_data = filter_zip(df, sel_zipcode) #asigned the filtered zipcode data to a variable for easier use

    st.write("Filtered Data:", filtered_data)
    st.header("Collection Days by Zipcode")

    recycle_chart = create_bar_chart(filtered_data, 'recollect', 'Recycles Collection Days') #created a barchart with my functions
    st.altair_chart(recycle_chart, use_container_width=True) #creating the chart with create bar chart as the argument
    trash_chart = create_bar_chart(filtered_data, 'trashday', 'Trash Collection Days') #same thing with the trashdays
    st.altair_chart(trash_chart, use_container_width=True) #the user container width is to make the graph the width of the streamlit app

#functions for third page (distrcit)
#filtering the df by district
def filter_district(df, selected_districts):
    return df[df['pwd_district'].isin(selected_districts)]


def gen_scatter_chart(data, xcol, ycol, title):
    scatter_chart = alt.Chart(data).mark_circle().encode( #creates charts with circles as data points
        x=f'{xcol}:N', #specifies x column from argument, categorical variable
        y=f'{ycol}:N', #same for y
        tooltip=[f'{xcol}:N', f'{ycol}:N'] #same for tooltip
    ).properties(
        title=title #title defined in argument
    )
    return scatter_chart #returns a scatterchart to be used for my altair chart for my 3rd page


def district_page():
    st.sidebar.title("Filter Data by District")
    df = loaddata()
    selected_districts = st.sidebar.multiselect("Select Districts", df['pwd_district'].unique()) #uses only the unique values for district seleciton
    filtered_data = filter_district(df, selected_districts) #filters the data based on the selected districts

    scatterplot_trash = gen_scatter_chart(filtered_data, 'trashday', 'pwd_district','Scatter Plot: Trash Collection Day') #creates scatterplot with filtered data
    scatterplot_recollect = gen_scatter_chart(filtered_data, 'recollect', 'pwd_district','Scatter Plot: Recycles Collection Day')#same for recollect

    st.subheader("Scatter Plots")
    st.altair_chart(scatterplot_trash, use_container_width=True) #prints scatterplots, makes them width of the streamlit app
    st.altair_chart(scatterplot_recollect, use_container_width=True)


def main():
    page = st.sidebar.selectbox("Select a page", ["Filter by Address", "Filter by Zipcode", "Filter by District"])
    if page == "Filter by Address": #if function to decided what page we are on
        page1() #title function for first page
        st.sidebar.write("Choose Options to Display Data")
        mn = st.sidebar.multiselect("Select a neighborhood:  ", all_mn()) #using the functions created before i found out about ".unique" for the selection
        day = st.sidebar.multiselect("Select day for trash collection", all_days())

        generate_map(mn, day) #generating map based on mailing neighborhood and/or day selected
        data = filter_data(mn, day)
        counts = count_mn(mn, data) #filter data and count function to generate the piechart
        st.pyplot(gen_pie_chart(counts, mn)) #generating pie chart using function
        gen_pie_chart(counts, mn)

        gen_bar_chart(mn, day) #generating bar chart using function
        st.pyplot(gen_bar_chart(mn, day))


    elif page == "Filter by Zipcode":
        page2()
        zipcode_page() #using page function created to write the page



    elif page == "Filter by District":
        page3()
        district_page() #page function create to write the page


main()

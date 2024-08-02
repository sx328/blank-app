import streamlit as st
import pandas as pd
import pydeck as pdk
import geopandas as gpd

# List of US state abbreviations to filter the data
us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
             'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
             'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
             'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
             'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

# Title of the app
st.title('Order Data Analysis')

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Read data from the uploaded CSV file
    data = pd.read_csv(uploaded_file)

    try:
        # Convert 'Created at' to datetime, considering timezone
        data['Created at'] = pd.to_datetime(data['Created at'], utc=True)
        data['Month-Year'] = data['Created at'].dt.to_period('M')

        # Ensure the 'Billing Province' column is treated as state data
        data['Billing Province'] = data['Billing Province'].str.upper()
        filtered_data = data[data['Billing Province'].isin(us_states)]

        # Display filtered data to check the 'Billing Province' content
        st.write("Filtered Data by US States:", filtered_data.head())

        # Aggregate shipment counts by state for mapping
        shipment_counts = filtered_data['Billing Province'].value_counts().reset_index()
        shipment_counts.columns = ['state', 'count']
        
        # Check if any state data is available for mapping
        if shipment_counts.empty:
            st.error("No valid US state data found in the 'Billing Province' column.")
        else:
            # Load US states GeoJSON data
            us_states_geojson = gpd.read_file('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')
            
            # Merge shipment counts with GeoJSON data
            merged_data = us_states_geojson.merge(shipment_counts, left_on='id', right_on='state', how='left')
            merged_data['count'] = merged_data['count'].fillna(0)
            
            # Normalize counts
            max_count = merged_data['count'].max()
            merged_data['count_normalized'] = merged_data['count'] / max_count

            # Define the layer for the choropleth map
            layer = pdk.Layer(
                "GeoJsonLayer",
                merged_data,
                opacity=0.8,
                stroked=False,
                filled=True,
                extruded=True,
                wireframe=True,
                get_elevation="count * 100",
                get_fill_color="[255 * (1 - count_normalized), 255 * count_normalized, 0]",
                get_line_color=[255, 255, 255],
                pickable=True,
            )

            # Set the view location and zoom level for the map
            view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3, pitch=45)

            # Render the deck.gl map in Streamlit
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{name}: {count} shipments"}
            ))

    except pd.errors.OutOfBoundsDatetime:
        st.error("Error: Out of bounds datetime - check date formats in 'Created at'")
    except ValueError:
        st.error("Error: Invalid date format in 'Created at'")
    except KeyError as e:
        st.error(f"Missing column in data: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
import streamlit as st
import pandas as pd
import pydeck as pdk

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
        data['Created at'] = pd.to_datetime(data['Created at'], utc=True, format='%Y-%m-%d %H:%M:%S %z')
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
            max_count = shipment_counts['count'].max()
            shipment_counts['count_normalized'] = shipment_counts['count'] / max_count

            # Define the layer for the choropleth map
            layer = pdk.Layer(
                "ChoroplethLayer",
                shipment_counts,
                get_polygon="https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
                get_fill_color="[255 * (1 - count_normalized), 255 * (1 - count_normalized), 255 * (1 - count_normalized)]",
                get_line_color="[255, 255, 255]",
                pickable=True,
                auto_highlight=True
            )

            # Set the view location and zoom level for the map
            view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3)

            # Render the deck.gl map in Streamlit
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v9',
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{state}: {count} shipments"}
            ))

    except pd.errors.OutOfBoundsDatetime:
        st.error("Error: Out of bounds datetime - check date formats in 'Created at'")
    except ValueError:
        st.error("Error: Invalid date format in 'Created at'")
    except KeyError as e:
        st.error(f"Missing column in data: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

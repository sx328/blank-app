import streamlit as st
import pandas as pd

# Title of the app
st.title('Order Data Analysis')

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Read data from the uploaded CSV file
    data = pd.read_csv(uploaded_file)

    # Try converting 'Created at' to datetime including parsing of timezone
    try:
        data['Created at'] = pd.to_datetime(data['Created at'], utc=True, format='%Y-%m-%d %H:%M:%S %z')
        data['Month-Year'] = data['Created at'].dt.to_period('M')

        # Display the uploaded dataframe
        st.write("Uploaded Data:", data.head())

        # Calculating the average items per order
        avg_items_per_order = data['Lineitem quantity'].mean()
        st.write(f"Average Items per Order: {avg_items_per_order:.2f}")

        # Calculating the average order value
        avg_order_value = data['Total'].mean()
        st.write(f"Average Order Value: ${avg_order_value:.2f}")

        # Calculating the count of orders per month
        orders_per_month = data.groupby('Month-Year').size()

        # Creating a DataFrame for the line chart
        chart_data = pd.DataFrame({
            "Month": orders_per_month.index.astype(str),
            "Number of Orders": orders_per_month.values
        }).set_index('Month')

        # Plotting the line chart for Number of Orders Per Month
        st.line_chart(chart_data)
        st.write("> Note: the latest month's data could be incomplete.")

    except pd.errors.OutOfBoundsDatetime:
        st.error("Error: Out of bounds datetime - check date formats in 'Created at'")
    except ValueError:
        st.error("Error: Invalid date format in 'Created at'")
    except KeyError as e:
        st.error(f"Missing column in data: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

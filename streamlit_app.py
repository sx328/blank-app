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

        # Calculating the average orders per month
        avg_orders_per_month = data.groupby('Month-Year').size().mean()
        st.write(f"Average Orders per Month: {avg_orders_per_month:.2f}")

        # Calculating the average order value per month for the line chart
        monthly_order_values = data.groupby('Month-Year')['Total'].mean().sort_index()

        # Creating a DataFrame for the line chart
        chart_data = pd.DataFrame({
            "Month": monthly_order_values.index.astype(str),
            "Average Order Value": monthly_order_values.values
        }).set_index('Month')

        # Plotting the line chart for Average Order Value Over Time
        st.line_chart(chart_data)

    except pd.errors.OutOfBoundsDatetime:
        st.error("Error: Out of bounds datetime - check date formats in 'Created at'")
    except ValueError:
        st.error("Error: Invalid date format in 'Created at'")
    except KeyError as e:
        st.error(f"Missing column in data: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

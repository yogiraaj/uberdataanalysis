from flask import Flask, render_template, request
import pandas as pd
import preprocessor
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

app = Flask(__name__)

fact_table = None  # Initialize fact_table as a global variable

def generate_plot(data):
    # Create a 2x2 grid for subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))

    # Plot Vendor ID distribution
    sns.countplot(x='VendorID', data=data, ax=axes[0, 0])
    axes[0, 0].set_title('Distribution of Vendor IDs')

    # Plot Passenger Count distribution
    sns.countplot(x='passenger_count_id', data=data, palette="viridis", order=[1, 2, 3, 4, 5], ax=axes[0, 1])
    axes[0, 1].set_title('Passenger Count Distribution')

    # Plot Rate Code distribution
    sns.countplot(x='rate_code_id', data=data, palette="viridis", order=[1, 2, 3, 4, 5], ax=axes[1, 0])
    axes[1, 0].set_title('Distribution of Rate Code IDs')

    # Map payment type IDs to labels
    payment_type_labels = {
        1: 'Credit Card',
        2: 'Cash',
        3: 'No Charge',
        4: 'Dispute'
    }

    # Map payment type IDs to labels and plot Payment Type distribution
    data['payment_type_label'] = data['payment_type_id'].map(payment_type_labels)
    sns.countplot(x='payment_type_label', data=data, palette="viridis", ax=axes[1, 1])
    axes[1, 1].set_title('Distribution of Payment Types')

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Encode the plot as base64
    plot_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    return plot_base64



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    global fact_table

    uploaded_file = request.files['file']

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        fact_table = preprocessor.preprocessor(data)
        overall_results = analyze_overall(fact_table)
        plot_base64 = generate_plot(fact_table)
        vendor_buttons = get_vendor_buttons(fact_table)
        return render_template('analysis.html', overall_results=overall_results, plot_base64=plot_base64, vendor_buttons=vendor_buttons, fact_table=fact_table)

    return render_template('analysis.html', overall_results=None, plot_base64=None, vendor_buttons=None)

@app.route('/analyze_vendor', methods=['POST'])
def analyze_vendor():
    try:
        selected_vendor_id = int(request.form['selected_vendor_id'])
        uploaded_file = request.files['file']

        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            fact_table = preprocessor.preprocessor(data)

            if selected_vendor_id == 1:
                subset_data = fact_table[fact_table['VendorID'] == 1]
            elif selected_vendor_id == 2:
                subset_data = fact_table[fact_table['VendorID'] == 2]
            # Add more conditions for other vendor IDs if needed

            plot_base64 = generate_plot(subset_data)
            return render_template('analysis_vendor.html', vendor_id=selected_vendor_id, plot_base64=plot_base64)

    except Exception as e:
        print(e)
        return render_template('error.html')  # Create an error.html template for displaying error messages



def analyze_overall(data):
    total_amount_sum = data['total_amount'].sum()
    avg_fare_amt = data['fare_amount'].mean()
    avg_trip_distance = data['trip_distance_id'].mean()

    return {
        'total_amount_sum': total_amount_sum,
        'avg_fare_amt': avg_fare_amt,
        'avg_trip_distance': avg_trip_distance,
    }

def get_vendor_buttons(data):
    vendor_ids = data['VendorID'].unique()
    return vendor_ids.tolist()

if __name__ == '__main__':
    app.run(debug=True)

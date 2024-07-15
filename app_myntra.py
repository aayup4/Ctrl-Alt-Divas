from flask import Flask, render_template, request, url_for
import os
import pandas as pd
from PIL import Image

app = Flask(__name__)

# Define base directory and category directories
base_dir = 'C:/Users/Yashvi/Hackerramp/static'  # Use forward slashes for the base directory
bottoms_dir = os.path.join(base_dir, 'bottoms').replace('\\', '/')
tops_dir = os.path.join(base_dir, 'tops').replace('\\', '/')
shoes_dir = os.path.join(base_dir, 'shoes').replace('\\', '/')
jewellery_dir = os.path.join(base_dir, 'jewellery').replace('\\', '/')

# Function to get image URLs from directories
def get_image_urls(base_dir):
    data = {}
    categories = os.listdir(base_dir)
    for category in categories:
        category_path = os.path.join(base_dir, category).replace('\\', '/')
        if os.path.isdir(category_path):
            images = [os.path.join(category_path, img).replace('\\', '/') for img in os.listdir(category_path) if img.endswith('.jpg')]
            data[category] = images
    return data

# Function to get top N recommendations based on similarity
def get_top_n_recommendations(similarities_df, selected_item, n, category2, directory, subcategory=None):
    selected_item_basename = os.path.basename(selected_item)
    filtered_df = similarities_df[(similarities_df['item1'] == selected_item_basename) & (similarities_df['category2'] == category2)]
    if subcategory and 'subcategory2' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['subcategory2'] == subcategory]
    sorted_df = filtered_df.sort_values(by='similarity', ascending=False)
    top_n_recommendations = sorted_df.head(n)
    return [os.path.join(directory, item).replace('\\', '/') for item in top_n_recommendations['item2'].values.tolist()]

# Load similarities from CSV
similarities_csv_path = os.path.join('C:/Users/Yashvi/Hackerramp/processed_dataset', 'all_categories_similarities.csv')
similarities_df = pd.read_csv(similarities_csv_path)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    data = get_image_urls(base_dir)
    selected_bottom = None
    recommended_tops = []
    recommended_shoes = []
    recommended_jewellery = []

    if request.method == 'POST' and 'bottom' in request.files:
        bottom_file = request.files['bottom']
        if bottom_file.filename != '':
            bottom_path = os.path.join(bottoms_dir, bottom_file.filename).replace('\\', '/')
            bottom_file.save(bottom_path)
            selected_bottom = bottom_path

            # Get recommendations for tops, shoes, and jewellery
            n = 5  # Number of recommendations
            tops_type = request.form.get('tops_type')
            shoes_type = request.form.get('shoes_type')

            recommended_tops = get_top_n_recommendations(similarities_df, selected_bottom, n, 'tops', tops_dir, tops_type)
            recommended_shoes = get_top_n_recommendations(similarities_df, selected_bottom, n, 'shoes', shoes_dir, shoes_type)
            recommended_jewellery = get_top_n_recommendations(similarities_df, selected_bottom, n, 'jewellery', jewellery_dir)

    return render_template('index.html', data=data, selected_bottom=selected_bottom,
                           recommended_tops=recommended_tops, recommended_shoes=recommended_shoes, recommended_jewellery=recommended_jewellery)

if __name__ == '__main__':
    app.run(debug=True)
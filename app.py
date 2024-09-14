from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import os
from datetime import datetime  # Make sure this line is included

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Load the pre-trained model (ensure the model is already trained and saved)
model = load_model('plant_disease_prediction_model.h5')

# Class names corresponding to the plant diseases (complete list from Plant Village)
class_names = [
    'Tomato Late Blight', 'Tomato Healthy', 'Grape Healthy', 'Orange Huanglongbing (Citrus Greening)',
    'Soybean Healthy', 'Squash Powdery Mildew', 'Potato Healthy', 'Corn Northern Leaf Blight',
    'Tomato Early Blight', 'Tomato Septoria Leaf Spot', 'Corn Cercospora Leaf Spot', 'Strawberry Leaf Scorch',
    'Peach Healthy', 'Apple Scab', 'Tomato Yellow Leaf Curl Virus', 'Tomato Bacterial Spot',
    'Apple Black Rot', 'Blueberry Healthy', 'Cherry Powdery Mildew', 'Peach Bacterial Spot',
    'Apple Cedar Apple Rust', 'Tomato Target Spot', 'Pepper Healthy', 'Grape Leaf Blight',
    'Potato Late Blight', 'Tomato Mosaic Virus', 'Strawberry Healthy', 'Apple Healthy',
    'Grape Black Rot', 'Potato Early Blight', 'Cherry Healthy', 'Corn Common Rust', 'Grape Esca (Black Measles)',
    'Raspberry Healthy', 'Tomato Leaf Mold', 'Tomato Spider Mites', 'Pepper Bacterial Spot', 'Corn Healthy'
]

# Sample data for demonstration (replace with your database or data source)
diseases = {
    "powdery mildew": {
        "info": (
            "Symptoms: White or grayish powdery spots on leaves, stems, and buds. It often begins on the upper side of leaves and can spread rapidly.\n"
            "Conditions: Thrives in warm, dry environments with high humidity. It can be exacerbated by poor air circulation.\n"
            "Impact: Reduces photosynthesis, weakens plants, and can lead to stunted growth and reduced yield.\n"
            "Management: Improve air circulation, avoid overhead watering, and apply fungicides if needed."
        ),
        "image": "images/pow.jpeg"
    },
    "rust": {
        "info": (
            "Symptoms: Orange, red, yellow, or brown pustules on leaves, stems, and sometimes fruits. The pustules can burst open, releasing spores.\n"
            "Conditions: Prefers warm, humid conditions and can spread rapidly through wind and rain.\n"
            "Impact: Can cause significant defoliation, reducing plant vigor and yield.\n"
            "Management: Remove and destroy infected plant material, use resistant varieties, and apply appropriate fungicides."
        ),
        "image": "images/rusts.jpg"
    },
    "downy mildew": {
        "info": (
            "Symptoms: Yellow or white patches on the underside of leaves, often accompanied by a downy or fuzzy appearance.\n"
            "Conditions: Thrives in cool, damp environments. High humidity and poor airflow can exacerbate the problem.\n"
            "Impact: Leads to leaf drop, reduced plant growth, and poor fruit development.\n"
            "Management: Improve ventilation, avoid overhead watering, and use fungicides designed for downy mildew."
        ),
        "image": "images/downy.png"
    },
    "blight": {
        "info": (
            "Symptoms: Rapid death of plant tissues, often leading to dark, water-soaked spots or lesions on leaves, stems, or fruits.\n"
            "Conditions: Can occur in both warm and cool weather, with moisture playing a key role in its development.\n"
            "Impact: Can lead to significant yield losses and reduced plant health.\n"
            "Management: Remove and destroy infected plant material, avoid overhead watering, and use disease-resistant varieties."
        ),
        "image": "images/blight.jpeg"
    },
    "leaf spot": {
        "info": (
            "Symptoms: Small, round, or irregular spots on leaves, which can be black, brown, or gray, often with a yellow halo.\n"
            "Conditions: Caused by various fungi or bacteria; can spread in conditions of high humidity and poor airflow.\n"
            "Impact: Reduces photosynthesis and overall plant health.\n"
            "Management: Improve air circulation, use fungicides if necessary, and avoid overhead watering."
        ),
        "image": "images/leaf_spot.jpeg"
    },
    "root rot": {
        "info": (
            "Symptoms: Wilting, yellowing leaves, and a foul smell from the soil. Roots may appear dark and mushy.\n"
            "Conditions: Caused by various fungi in poorly drained soils or excessive watering conditions.\n"
            "Impact: Leads to plant decline and can cause the plant to die if not managed properly.\n"
            "Management: Improve soil drainage, avoid overwatering, and consider using fungicides."
        ),
        "image": "images/root.jpeg"
    },
    "mosaic virus": {
        "info": (
            "Symptoms: Mottled or streaked patterns on leaves, which can be green, yellow, or light brown. The plant may exhibit stunted growth.\n"
            "Conditions: Spread by insects or contaminated tools. Thrives in warm, dry conditions.\n"
            "Impact: Leads to reduced plant growth and poor fruit development.\n"
            "Management: Control insect vectors, use disease-free seeds or plants, and remove infected plants."
        ),
        "image": "images/mosaic_virus.jpeg"
    },
    "scab": {
        "info": (
            "Symptoms: Rough, sunken lesions on fruits, leaves, or stems, often with a scabby appearance.\n"
            "Conditions: Caused by fungal or bacterial pathogens, commonly in humid conditions.\n"
            "Impact: Affects the appearance and quality of fruits and leaves, potentially reducing yield.\n"
            "Management: Remove and destroy infected material, improve air circulation, and apply appropriate fungicides."
        ),
        "image": "images/scab.jpeg"
    },
    "sclerotinia": {
        "info": (
            "Symptoms: Soft rot in flowers, stems, and fruits, often with a white, cottony mold on infected areas.\n"
            "Conditions: Thrives in cool, damp conditions, particularly in high humidity.\n"
            "Impact: Can cause severe decay and reduce plant yield and quality.\n"
            "Management: Improve ventilation, avoid overhead watering, and apply fungicides."
        ),
        "image": "images/sclerotinia.jpeg"
    },
    "early blight": {
        "info": (
            "Symptoms: Dark, concentric rings on leaves, which can lead to early leaf drop and reduced plant health.\n"
            "Conditions: Prefers warm, moist environments; commonly affects tomatoes and potatoes.\n"
            "Impact: Can significantly reduce plant yield and vigor.\n"
            "Management: Remove and destroy infected leaves, improve air circulation, and apply fungicides."
        ),
        "image": "images/early_blight.jpeg"
    },
    "late blight": {
        "info": (
            "Symptoms: Dark, water-soaked lesions on leaves, stems, and fruits, often leading to rapid decay.\n"
            "Conditions: Thrives in cool, wet conditions; affects potatoes and tomatoes.\n"
            "Impact: Causes rapid plant collapse and significant yield loss.\n"
            "Management: Remove and destroy infected plants, use resistant varieties, and apply fungicides."
        ),
        "image": "images/late_blight.jpeg"
    },
    "fusarium wilt": {
        "info": (
            "Symptoms: Wilting, yellowing leaves, and stunted growth due to vascular system infection.\n"
            "Conditions: Caused by a soil-borne fungus; thrives in warm conditions.\n"
            "Impact: Reduces plant health and can lead to plant death if untreated.\n"
            "Management: Use resistant varieties, improve soil drainage, and consider soil treatments."
        ),
        "image": "images/fusarium.jpeg"
    },
    "anthracnose": {
        "info": (
            "Symptoms: Dark, sunken lesions on leaves, stems, and fruits, often with a reddish or brown color and concentric rings.\n"
            "Conditions: Prefers warm, wet conditions; can spread through rain and wind.\n"
            "Impact: Reduces plant health and yield, leading to poor quality produce.\n"
            "Management: Remove and destroy infected material, improve air circulation, and apply fungicides."
        ),
        "image": "images/anthracnose.jpeg"
    },
    "canker": {
        "info": (
            "Symptoms: Sunken, necrotic lesions on stems, branches, or trunks, often caused by fungi or bacteria.\n"
            "Conditions: Can occur in various weather conditions; spread through wounds or infected material.\n"
            "Impact: Weakens plant structure and can lead to death if severe.\n"
            "Management: Prune and destroy infected parts, use appropriate fungicides, and avoid wounding plants."
        ),
        "image": "images/canker.png"
    },
    "nematode infestation": {
        "info": (
            "Symptoms: Stunted growth, yellowing leaves, and poor plant development due to root damage.\n"
            "Conditions: Parasitic worms infect plant roots, often in poorly managed soils.\n"
            "Impact: Reduces plant vigor and yield; can be severe in high infestations.\n"
            "Management: Use nematode-resistant plant varieties, improve soil health, and consider soil treatments."
        ),
        "image": "images/nematode_infestion.jpeg"
    },
    "bacterial spot": {
        "info": (
            "Symptoms: Small, dark, water-soaked spots on leaves and fruits, often leading to early leaf drop and reduced fruit quality.\n"
            "Conditions: Caused by bacteria; thrives in warm, humid conditions and spreads through rain and wind.\n"
            "Impact: Reduces plant health and fruit quality.\n"
            "Management: Remove and destroy infected material, improve air circulation, and apply bactericides if necessary."
        ),
        "image": "images/bacterial_spot.jpeg"
    },
    "gray mold": {
        "info": (
            "Symptoms: Fuzzy, grayish mold on infected plant parts, particularly in humid conditions.\n"
            "Conditions: Caused by the fungus Botrytis cinerea; thrives in cool, damp environments.\n"
            "Impact: Affects flowers, fruits, and foliage, leading to decay and reduced quality.\n"
            "Management: Improve air circulation, avoid overhead watering, and apply fungicides."
        ),
        "image": "images/gray_mold.jpeg"
    },
    "powdery scab": {
        "info": (
            "Symptoms: Powdery, scabby lesions on tubers, particularly potatoes.\n"
            "Conditions: Occurs in cool, damp environments; can spread through infected seed tubers.\n"
            "Impact: Affects the appearance and quality of tubers, reducing market value.\n"
            "Management: Use disease-free seed tubers, improve soil drainage, and apply appropriate treatments."
        ),
        "image": "images/powdery_scab.jpeg"
    },
    "bacterial wilt": {
        "info": (
            "Symptoms: Wilting, yellowing, and eventual death of the plant due to vascular infection by bacteria.\n"
            "Conditions: Caused by soil-borne bacteria; thrives in warm, wet conditions.\n"
            "Impact: Leads to rapid plant collapse and significant yield loss.\n"
            "Management: Use resistant varieties, practice crop rotation, and manage soil moisture."
        ),
        "image": "images/bacterial.jpeg"
    },
    "phytophthora blight": {
        "info": (
            "Symptoms: Water-soaked lesions on leaves and stems, often leading to rapid plant collapse.\n"
            "Conditions: Caused by a soil-borne pathogen; thrives in warm, wet conditions.\n"
            "Impact: Can cause severe plant collapse and yield loss.\n"
            "Management: Improve drainage, avoid excessive watering, and apply targeted fungicides."
        ),
        "image": "images/phytophthora_blight.jpeg"
    },
    "septoria leaf spot": {
        "info": (
            "Symptoms: Small, round, dark spots with light centers on leaves, leading to early leaf drop.\n"
            "Conditions: Prefers moist, humid conditions; spread through rain and wind.\n"
            "Impact: Reduces plant health and yield; can lead to premature leaf drop.\n"
            "Management: Remove infected leaves, improve air circulation, and apply fungicides."
        ),
        "image": "images/septoria_leaf_spot.jpeg"
    },
    "verticillium wilt": {
        "info": (
            "Symptoms: Yellowing and wilting of leaves, often with a characteristic pattern of necrosis due to vascular infection.\n"
            "Conditions: Caused by a soil-borne fungus; affects plants in warm, well-drained soils.\n"
            "Impact: Reduces plant health and can lead to plant death if severe.\n"
            "Management: Use resistant varieties, practice crop rotation, and improve soil management."
        ),
        "image": "images/verticillium.jpeg"
    },
    "alterna leaf spot": {
        "info": (
            "Symptoms: Irregular, dark brown to black spots with concentric rings on leaves, which can lead to premature leaf drop.\n"
            "Conditions: Caused by a fungal pathogen; thrives in warm, moist environments.\n"
            "Impact: Can lead to reduced plant health and yield.\n"
            "Management: Improve air circulation, remove infected leaves, and use appropriate fungicides."
        ),
        "image": "images/alterna_leaf_spot.jpeg"
    }
}

def process_image(image_path):
    image = Image.open(image_path).resize((224, 224))  # Resize to match the model's input size
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnose')
def diagnose():
    return render_template('diagnose.html')

@app.route('/fertilizer')
def fertilizer():
    return render_template('fertilizer.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/article')
def article():
    return render_template('article.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        image_path = os.path.join('static/uploads', file.filename)
        file.save(image_path)

        # Preprocess the image
        img_array = process_image(image_path)
        print(f"Image preprocessed: {img_array.shape}")

        # Get model predictions
        predictions = model.predict(img_array)
        confidence = float(np.max(predictions))  # Convert to Python native float
        predicted_class = class_names[np.argmax(predictions[0])]

        # Set a confidence threshold
        if confidence < 0.5:
            predicted_class = 'Unknown'
            recommendation = "No disease detected. Please upload a clear image of the plant."
        else:
            recommendation = get_recommendation(predicted_class)

        return jsonify({'disease': predicted_class, 'confidence': confidence, 'recommendation': recommendation})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search_disease', methods=['POST'])
def search_disease():
    search_query = request.form.get('search_query', '').strip().lower()

    if not search_query:
        flash('Please enter a search term.')
        return redirect(url_for('index'))

    disease_data = diseases.get(search_query)
    if disease_data:
        disease_info = disease_data['info']
        disease_image = url_for('static', filename=disease_data['image'])  # Get image URL
        return render_template('index.html', disease_info=disease_info, disease_image=disease_image)
    else:
        flash('Disease not found. Please try another search term.')
        return redirect(url_for('index'))

# Updated Planting Suggestions based on season and region
PLANTING_SUGGESTIONS = {
    'spring': {
        'north': ['Tomato', 'Peas', 'Carrot', 'Radish', 'Spinach', 'Cauliflower', 'Lettuce'],
        'south': ['Chili Peppers', 'Okra', 'Eggplant', 'Cucumber', 'Bitter Gourd', 'Pumpkin'],
        'east': ['Potato', 'Tomato', 'Cauliflower', 'Cabbage', 'Spinach', 'Brinjal'],
        'west': ['Cucumber', 'Bottle Gourd', 'Pumpkin', 'Zucchini', 'Squash', 'Chili Peppers'],
        'central': ['Tomato', 'Onion', 'Beetroot', 'Spinach', 'Fenugreek', 'Peas'],
        'general': ['Tomato', 'Lettuce', 'Carrot']  # Default for unspecified regions
    },
    'summer': {
        'north': ['Corn', 'Cucumber', 'Bitter Gourd', 'Tomato', 'Chili', 'Brinjal', 'Melons'],
        'south': ['Sweet Potato', 'Banana', 'Yam', 'Papaya', 'Snake Gourd', 'Drumstick'],
        'east': ['Okra', 'Brinjal', 'Tomato', 'Cucumber', 'Watermelon', 'Pumpkin'],
        'west': ['Sunflower', 'Groundnut', 'Okra', 'Bitter Gourd', 'Tomato', 'Melons'],
        'central': ['Tomato', 'Cucumber', 'Bottle Gourd', 'Chili', 'Capsicum', 'Brinjal'],
        'general': ['Corn', 'Cucumber', 'Squash']
    },
    'fall': {
        'north': ['Pumpkin', 'Broccoli', 'Garlic', 'Spinach', 'Beetroot', 'Cabbage'],
        'south': ['Amaranth', 'Chili', 'Brinjal', 'Spinach', 'Bitter Melon', 'Snake Gourd'],
        'east': ['Spinach', 'Turnip', 'Mustard Greens', 'Radish', 'Cauliflower', 'Cabbage'],
        'west': ['Mustard Greens', 'Cabbage', 'Cauliflower', 'Radish', 'Beetroot'],
        'central': ['Spinach', 'Garlic', 'Onion', 'Radish', 'Fenugreek', 'Cauliflower'],
        'general': ['Pumpkin', 'Broccoli', 'Spinach']
    },
    'winter': {
        'north': ['Kale', 'Garlic', 'Onion', 'Leeks', 'Peas', 'Carrots', 'Spinach'],
        'south': ['Cassava', 'Ginger', 'Taro', 'Radish', 'Spinach', 'Beetroot'],
        'east': ['Garlic', 'Onion', 'Kohlrabi', 'Cabbage', 'Broccoli', 'Spinach'],
        'west': ['Onion', 'Garlic', 'Beetroot', 'Turnips', 'Spinach', 'Carrots'],
        'central': ['Garlic', 'Onion', 'Spinach', 'Radish', 'Beetroot', 'Cauliflower'],
        'general': ['Kale', 'Brussels Sprouts', 'Garlic']
    }
}

def get_current_season():
    """Determine the current season based on the current date."""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10, 11]:
        return 'fall'
    else:
        return 'winter'

def get_season_from_month(month):
    """Determine the season based on the provided month."""
    if month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10, 11]:
        return 'fall'
    else:
        return 'winter'

def get_region_from_location(location):
    """Maps a user's location to a specific region of India."""
    location = location.lower()

    # Dictionary of regions
    regions = {
        'north': {
            'delhi': ['delhi'],
            'punjab': ['amritsar', 'barnala', 'bathinda', 'faridkot', 'fatehgarh sahib', 'fazilka', 'ferozepur', 'gurdaspur', 'jalandhar', 'kapurthala', 'ludhiana', 'mansa', 'moga', 'mohali', 'muktsar', 'patiala', 'rupnagar', 'sbs nagar', 'sangrur', 'tarn taran'],
            'uttar pradesh': ['agra', 'aligarh', 'ambedkar nagar', 'amethi', 'amroha', 'auraiya', 'ayodhya', 'azamgarh', 'badaun', 'bagpat', 'bahraich', 'ballia', 'balrampur', 'banda', 'barabanki', 'bareilly', 'basti', 'bhadohi', 'bijnor', 'budaun', 'bulandshahr', 'chandauli', 'chitrakoot', 'deoria', 'etah', 'etawah', 'faizabad', 'farrukhabad', 'fatehpur', 'fatehpur sikri', 'firozabad', 'gautam buddha nagar', 'ghaziabad', 'ghazipur', 'gonda', 'gorakhpur', 'hamirpur', 'hapur', 'hardoi', 'hathras', 'jalaun', 'jaunpur', 'jhansi', 'kannauj', 'kanpur', 'kaushambi', 'kheri', 'kushinagar', 'lalitpur', 'lucknow', 'maharajganj', 'mahoba', 'mainpuri', 'mathura', 'mau', 'meerut', 'mirzapur', 'moradabad', 'muzaffarnagar', 'pilibhit', 'pratapgarh', 'rae bareli', 'rampur', 'saharanpur', 'sant kabir nagar', 'sant ravi das nagar', 'shahjahanpur', 'shamli', 'shravasti', 'siddharthnagar', 'sitapur', 'sultanpur', 'unnao', 'varanasi'],
            'himachal pradesh': ['bilaspur', 'chamba', 'hamirpur', 'kangra', 'kinnaur', 'kullu', 'mandi', 'shimla', 'sirmaur', 'solan', 'una'],
            'haryana': ['ambala', 'bhiwani', 'faridabad', 'fatehabad', 'gurgaon', 'hisar', 'jind', 'jhajjar', 'jhanana', 'kaithal', 'karnal', 'kurukshetra', 'mahendragarh', 'mewat', 'panchkula', 'panipat', 'rewari', 'rohtak', 'sirsa', 'sonipat', 'yamunanagar'],
            'uttarakhand': ['almora', 'bageshwar', 'champawat', 'dehradun', 'haridwar', 'nainital', 'pauri garhwal', 'pithoragarh', 'rudraprayag', 'tehri garhwal', 'udham singh nagar', 'uttarkashi'],
            'jammu and kashmir': ['jammu', 'kathua', 'poonch', 'rajouri', 'samba', 'udhampur', 'anantnag', 'bandipora', 'baramulla', 'budgam', 'doda', 'ganderbal', 'kargil', 'kishtwar', 'kulgam', 'pulwama', 'ramban', 'reasi', 'samba', 'shopian', 'srinagar', 'udhampur']
        },
        'south': {
            'tamil nadu': ['chennai', 'coimbatore', 'cuddalore', 'dharmapuri', 'dindigul', 'erode', 'kanchipuram', 'kanyakumari', 'karur', 'madurai', 'nagapattinam', 'namakkal', 'perambalur', 'pudukkottai', 'ramanathapuram', 'salem', 'sivaganga', 'thanjavur', 'theni', 'thoothukudi', 'tiruchirappalli', 'tirunelveli', 'tirupur', 'vellore', 'viluppuram', 'virudhunagar'],
            'kerala': ['ernakulam', 'idukki', 'kannur', 'kasaragod', 'kottayam', 'kozhikode', 'malappuram', 'palakkad', 'pathanamthitta', 'thrissur', 'wayanad'],
            'karnataka': ['bagalkot', 'bangalore rural', 'bangalore urban', 'belagavi', 'bellary', 'bidar', 'chamarajanagar', 'chikballapur', 'chikmagalur', 'chitradurga', 'dakshina kannada', 'davangere', 'dharwad', 'gadag', 'gulbarga', 'hassan', 'haveri', 'kodagu', 'kolar', 'koppal', 'mandya', 'mysore', 'raichur', 'ramanagara', 'shivamogga', 'tumkur', 'udupi', 'uttara kannada', 'yadgir'],
            'andhra pradesh': ['adilabad', 'anantapur', 'chittoor', 'east godavari', 'guntur', 'krishna', 'kurnool', 'nellore', 'prakasam', 'srikakulam', 'visakhapatnam', 'vizianagaram', 'west godavari', 'ysr kadapa'],
            'telangana': ['adilabad', 'bhadradri kothagudem', 'hyderabad', 'jagtial', 'jangoan', 'jaya shankar bhupalpally', 'jogulamba gadwal', 'kamareddy', 'karimnagar', 'khammam', 'mahabubabad', 'mahabubnagar', 'mancherial', 'medak', 'medchal', 'nagarkurnool', 'nalgonda', 'narayanpet', 'nirmal', 'nizamabad', 'peddapalli', 'rajanna sircilla', 'rangareddy', 'warangal', 'warangal (rural)', 'warangal (urban)']
        },
        'east': {
            'west bengal': ['alipurduar', 'bankura', 'bardhaman', 'birbhum', 'dakshin dinajpur', 'darjeeling', 'hooghly', 'howrah', 'jalpaiguri', 'jhargram', 'kalimpong', 'kolkata', 'malda', 'murshidabad', 'nadia', 'north 24 parganas', 'paschim bardhaman', 'paschim medinipur', 'purba bardhaman', 'purba medinipur', 'purulia', 'south 24 parganas', 'uttar dinajpur'],
            'odisha': ['angul', 'bargarh', 'balangir', 'balasore', 'boudh', 'cuttack', 'dhenkanal', 'gajapati', 'ganjam', 'jagatsinghpur', 'jajpur', 'jharsuguda', 'kalahandi', 'kandhamal', 'kendrapara', 'kendujhar', 'khurda', 'koraput', 'malkangiri', 'nayagarh', 'nuapada', 'puri', 'rayagada', 'sambalpur', 'sonepur', 'sundargarh'],
            'assam': ['baksa', 'barpeta', 'bongaigaon', 'cachar', 'chirang', 'darrang', 'dhemaji', 'dhubri', 'dibrugarh', 'goalpara', 'golaghat', 'hailakandi', 'jorhat', 'karbi anglong', 'karimganj', 'kokrajhar', 'lakhimpur', 'majuli', 'morigaon', 'nagaon', 'nalbari', 'sivasagar', 'sonitpur', 'tinsukia', 'udalguri'],
            'bihar': ['araria', 'arwal', 'aurangabad', 'bhojpur', 'buxar', 'darbhanga', 'gaya', 'jehanabad', 'kaimur', 'katihar', 'khagaria', 'kishanganj', 'laukahi', 'madhepura', 'madhubani', 'munger', 'muzaffarpur', 'nalanda', 'nawada', 'purnia', 'rohtas', 'saran', 'sheikhpura', 'sheohar', 'sitamarhi', 'siwan', 'supaul', 'vaishali', 'west champaran', 'samastipur', 'gopalganj', 'bhagalpur', 'saran'],
            'jharkhand': ['bokaro', 'chatra', 'deoghar', 'dhanbad', 'dumka', 'east singhbhum', 'garhwa', 'giridih', 'godda', 'gumla', 'hazaribagh', 'jamtara', 'khunti', 'koderma', 'latehar', 'lohardaga', 'palamu', 'pakur', 'ramgarh', 'ranchi', 'sahibganj', 'seraikela kharsawan', 'west singhbhum'],
            'sikkim': ['east sikkim', 'north sikkim', 'south sikkim', 'west sikkim']
        },
        'west': {
            'goa': ['north goa', 'south goa'],
            'gujarat': ['ahmedabad', 'amreli', 'anand', 'banas kantha', 'baroda', 'bhavnagar', 'dangs', 'gandhinagar', 'jamnagar', 'junagadh', 'kutch', 'mehsana', 'narmada', 'navsari', 'panchmahal', 'patan', 'sabarkantha', 'surat', 'tapi', 'vadodara', 'valsad'],
            'maharashtra': ['ahmednagar', 'akola', 'amravati', 'aurangabad', 'beed', 'bhandara', 'buldhana', 'chandrapur', 'dhaulpur', 'gadchiroli', 'jalgaon', 'jalna', 'kolhapur', 'latur', 'mumbai', 'nagpur', 'nanded', 'nashik', 'osmanabad', 'palghar', 'parbhani', 'pune', 'raigad', 'ratnagiri', 'sangli', 'satara', 'solapur', 'thane', 'wardha', 'washim', 'yavatmal']
        }
    }

    # Iterate over the regions
    for region, locations in regions.items():
        for state, areas in locations.items():
            if location in areas:
                return region
    return 'Unknown Region'

@app.route('/seasonal', methods=['GET'])
def seasonal():
    return render_template('seasonal.html')

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    location = request.form.get('location', '').strip().lower()
    month = request.form.get('month')
    season_method = request.form.get('season_method')

    # Determine the current season automatically
    current_season = get_current_season()

    # Determine the season based on user input month or current season
    if season_method == 'manual' and month:
        try:
            month = int(month)
            if 1 <= month <= 12:
                season_from_month = get_season_from_month(month)
            else:
                raise ValueError("Month must be between 1 and 12.")
        except ValueError as e:
            print(f"Invalid month input: {month}. Error: {e}")
            season_from_month = current_season
            # Optionally, you might want to show an error message to the user here
    else:
        season_from_month = current_season

    # Determine the region based on location
    region = get_region_from_location(location)
    if region is None:
        print(f"Location not recognized: {location}")
        # region = 'general'  # Fallback to general suggestions if the location is not recognized

    # Use the determined season and region to get plant suggestions
    season_to_use = season_from_month
    suggestions = PLANTING_SUGGESTIONS.get(season_to_use, {}).get(region, [])

    no_suggestions = not suggestions  # Flag to indicate no suggestions are available

    return render_template('seasonal.html', suggestions=suggestions, no_suggestions=no_suggestions)

@app.route('/process-diagnosis', methods=['POST'])
def process_diagnosis():
    # Get form data
    plant_type = request.form['plant_type']
    placement = request.form['placement']
    location = request.form['location']
    temperature = float(request.form['temperature'])

    MAX_REALISTIC_TEMPERATURE = 50
    MIN_REALISTIC_TEMPERATURE = -10
    
    common_info = (f"Plant type: {plant_type}<br>"
               f"Placed: {placement}<br>"
               f"Location: {location}<br>"
               f"Temperature: {temperature}°C<br>")
    
    if temperature > MAX_REALISTIC_TEMPERATURE or temperature < MIN_REALISTIC_TEMPERATURE:
        result = f"Warning: The temperature of {temperature}°C is beyond typical plant stress levels and may not be realistic."
    elif plant_type == 'tomato' and (30 < temperature < 35):
        result = common_info + "<strong>Tomato plants may experience heat stress between 30°C and 35°C."
    elif plant_type == 'tomato' and (temperature > 40):
        result = common_info + "<strong>Tomato plants may experience severe stress above 40°C."
    elif plant_type == 'rose' and (5 < temperature < 15):
        result = common_info + "<strong>Rose plants may need protection from cold temperatures between 5°C and 15°C."
    elif plant_type == 'rose' and (temperature < 5):
        result = common_info + "<strong>Rose plants may face frost below 5°C."
    elif plant_type == 'wheat' and (5 < temperature < 10):
        result = common_info + "<strong>Wheat plants may experience growth issues between 5°C and 10°C."
    elif plant_type == 'wheat' and (temperature > 35):
        result = common_info + "<strong>Wheat plants may experience heat stress above 35°C."
    elif plant_type == 'carrot' and (25 < temperature < 30):
        result = common_info + "<strong>Carrot plants may suffer heat stress between 25°C and 30°C."
    elif plant_type == 'carrot' and (temperature > 35):
        result = common_info + "<strong>Carrot plants may suffer severe stress above 35°C."
    elif plant_type == 'lettuce' and (25 < temperature < 28):
        result = common_info + "<strong>Lettuce plants may bolt between 25°C and 28°C."
    elif plant_type == 'lettuce' and (temperature > 32):
        result = common_info + "<strong>Lettuce plants may suffer quality loss above 32°C."
    elif plant_type == 'cucumber' and (10 < temperature < 15):
        result = common_info + "<strong>Cucumber plants may need increased warmth between 10°C and 15°C."
    elif plant_type == 'cucumber' and (temperature > 30):
        result = common_info + "<strong>Cucumber plants may experience heat stress above 30°C."
    elif plant_type == 'pepper' and (15 < temperature < 20):
        result = common_info + "<strong>Pepper plants may have stunted growth between 15°C and 20°C."
    elif plant_type == 'pepper' and (temperature > 35):
        result = common_info + "<strong>Pepper plants may suffer from heat stress above 35°C."
    elif plant_type == 'corn' and (30 < temperature < 35):
        result = common_info + "<strong>Corn plants may experience heat stress between 30°C and 35°C."
    elif plant_type == 'corn' and (temperature > 38):
        result = common_info + "<strong>Corn plants may experience severe stress above 38°C."
    elif plant_type == 'spinach' and (25 < temperature < 30):
        result = common_info + "<strong>Spinach plants may bolt between 25°C and 30°C."
    elif plant_type == 'spinach' and (temperature > 32):
        result = common_info + "<strong>Spinach plants may experience leaf damage above 32°C."
    elif plant_type == 'potato' and (5 < temperature < 10):
        result = common_info + "<strong>Potato plants may experience slowed growth between 5°C and 10°C."
    elif plant_type == 'potato' and (temperature > 30):
        result = common_info + "<strong>Potato plants may experience heat stress above 30°C."
    elif plant_type == 'onion' and (25 < temperature < 30):
        result = common_info + "<strong>Onion plants may experience stress between 25°C and 30°C."
    elif plant_type == 'onion' and (temperature > 35):
        result = common_info + "<strong>Onion plants may experience severe heat stress above 35°C."
    elif plant_type == 'garlic' and (0 < temperature < 5):
        result = common_info + "<strong>Garlic plants may need protection from frost between 0°C and 5°C."
    elif plant_type == 'garlic' and (temperature > 30):
        result = common_info + "<strong>Garlic plants may suffer heat damage above 30°C."
    elif plant_type == 'bean' and (10 < temperature < 15):
        result = common_info + "<strong>Bean plants may suffer slow growth between 10°C and 15°C."
    elif plant_type == 'bean' and (temperature > 35):
        result = common_info + "<strong>Bean plants may experience heat stress above 35°C."
    elif plant_type == 'cabbage' and (25 < temperature < 28):
        result = common_info + "<strong>Cabbage plants may experience bolting between 25°C and 28°C."
    elif plant_type == 'cabbage' and (temperature > 32):
        result = common_info + "<strong>Cabbage plants may suffer heat stress above 32°C."
    elif plant_type == 'cauliflower' and (25 < temperature < 30):
        result = common_info + "<strong>Cauliflower plants may experience stress between 25°C and 30°C."
    elif plant_type == 'cauliflower' and (temperature > 35):
        result = common_info + "<strong>Cauliflower plants may experience heat damage above 35°C."
    elif plant_type == 'broccoli' and (10 < temperature < 15):
        result = common_info + "<strong>Broccoli plants may experience slow growth between 10°C and 15°C."
    elif plant_type == 'broccoli' and (temperature > 30):
        result = common_info + "<strong>Broccoli plants may experience heat stress above 30°C."
    elif plant_type == 'eggplant' and (15 < temperature < 20):
        result = common_info + "<strong>Eggplant plants may need increased warmth between 15°C and 20°C."
    elif plant_type == 'eggplant' and (temperature > 35):
        result = common_info + "<strong>Eggplant plants may suffer heat damage above 35°C."
    elif plant_type == 'squash' and (30 < temperature < 35):
        result = common_info + "<strong>Squash plants may suffer stress between 30°C and 35°C."
    elif plant_type == 'squash' and (temperature > 40):
        result = common_info + "<strong>Squash plants may experience severe heat stress above 40°C."
    elif plant_type == 'pumpkin' and (5 < temperature < 10):
        result = common_info + "<strong>Pumpkin plants may experience growth issues between 5°C and 10°C."
    elif plant_type == 'pumpkin' and (temperature > 35):
        result = common_info + "<strong>Pumpkin plants may experience stress above 35°C."
    elif plant_type == 'zucchini' and (25 < temperature < 30):
        result = common_info + "<strong>Zucchini plants may experience heat stress between 25°C and 30°C."
    elif plant_type == 'zucchini' and (temperature > 35):
        result = common_info + "<strong>Zucchini plants may experience severe stress above 35°C."
    elif plant_type == 'strawberry' and (5 < temperature < 10):
        result = common_info + "<strong>Strawberry plants may need protection from cold temperatures between 5°C and 10°C."
    elif plant_type == 'strawberry' and (temperature > 30):
        result = common_info + "<strong>Strawberry plants may experience heat stress above 30°C."
    elif plant_type == 'blueberry' and (10 < temperature < 15):
        result = common_info + "<strong>Blueberry plants may need protection from cold temperatures between 10°C and 15°C."
    elif plant_type == 'blueberry' and (temperature > 30):
        result = common_info + "<strong>Blueberry plants may suffer from heat stress above 30°C."
    elif plant_type == 'raspberry' and (0 < temperature < 5):
        result = common_info + "<strong>Raspberry plants may need protection from frost between 0°C and 5°C."
    elif plant_type == 'raspberry' and (temperature > 30):
        result = common_info + "<strong>Raspberry plants may experience stress above 30°C."
    elif plant_type == 'blackberry' and (25 < temperature < 30):
        result = common_info + "<strong>Blackberry plants may experience heat stress between 25°C and 30°C."
    elif plant_type == 'blackberry' and (temperature > 35):
        result = common_info + "<strong>Blackberry plants may experience severe stress above 35°C."
    elif plant_type == 'grape' and (10 < temperature < 15):
        result = common_info + "<strong>Grape plants may need protection from cold temperatures between 10°C and 15°C."
    elif plant_type == 'grape' and (temperature > 35):
        result = common_info + "<strong>Grape plants may suffer heat stress above 35°C."
    elif plant_type == 'apple' and (30 < temperature < 35):
        result = common_info + "<strong>Apple trees may experience stress between 30°C and 35°C."
    elif plant_type == 'apple' and (temperature > 40):
        result = common_info + "<strong>Apple trees may suffer severe heat damage above 40°C."
    elif plant_type == 'pear' and (5 < temperature < 10):
        result = common_info + "<strong>Pear trees may experience slowed growth between 5°C and 10°C."
    elif plant_type == 'pear' and (temperature > 30):
        result = common_info + "<strong>Pear trees may experience stress above 30°C."
    elif plant_type == 'peach' and (25 < temperature < 30):
        result = common_info + "<strong>Peach trees may suffer from heat stress between 25°C and 30°C."
    elif plant_type == 'peach' and (temperature > 35):
        result = common_info + "<strong>Peach trees may experience severe stress above 35°C."
    elif plant_type == 'plum' and (10 < temperature < 15):
        result = common_info + "<strong>Plum trees may need protection from cold temperatures between 10°C and 15°C."
    elif plant_type == 'plum' and (temperature > 30):
        result = common_info + "<strong>Plum trees may face heat stress above 30°C."
    elif plant_type == 'cherry' and (25 < temperature < 30):
        result = common_info + "<strong>Cherry trees may experience heat stress between 25°C and 30°C."
    elif plant_type == 'cherry' and (temperature > 35):
        result = common_info + "<strong>Cherry trees may suffer severe stress above 35°C."
    elif plant_type == 'apricot' and (5 < temperature < 10):
        result = common_info + "<strong>Apricot trees may need protection from cold temperatures between 5°C and 10°C."
    elif plant_type == 'apricot' and (temperature > 30):
        result = common_info + "<strong>Apricot trees may experience stress above 30°C."
    elif plant_type == 'fig' and (30 < temperature < 35):
        result = common_info + "<strong>Fig trees may suffer heat stress between 30°C and 35°C."
    elif plant_type == 'fig' and (temperature > 40):
        result = common_info + "<strong>Fig trees may experience severe damage above 40°C."
    elif plant_type == 'pomegranate' and (10 < temperature < 15):
        result = common_info + "<strong>Pomegranate trees may need protection from cold temperatures between 10°C and 15°C."
    elif plant_type == 'pomegranate' and (temperature > 35):
        result = common_info + "<strong>Pomegranate trees may suffer from heat stress above 35°C."
    elif plant_type == 'kiwi' and (10 < temperature < 15):
        result = common_info + "<strong>Kiwi plants may need increased warmth between 10°C and 15°C."
    elif plant_type == 'kiwi' and (temperature > 30):
        result = common_info + "<strong>Kiwi plants may suffer stress above 30°C."
    else:
        result = (f"Plant type: {plant_type}<br>"
          f"Placed: {placement}<br>"
          f"Location: {location}<br>"
          f"Temperature: {temperature}°C<br>"
          f"<strong>No major issues detected.<strong>")


    return render_template('result.html', result=result)

def get_recommendation(disease):
    recommendations = {
        'Tomato Late Blight': [
            'Apply fungicides.',
            'Use disease-resistant varieties.',
            'Remove and destroy infected plants.'
        ],
        'Tomato Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Ensure proper watering and fertilization.',
            'Monitor regularly for pests.'
        ],
        'Grape Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Prune vines regularly to improve air circulation.',
            'Ensure good soil drainage.'
        ],
        'Orange Huanglongbing (Citrus Greening)': [
            'There is no cure, remove infected trees.',
            'Control psyllid vectors with pesticides.',
            'Monitor new trees regularly for signs of infection.'
        ],
        'Soybean Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Watch for signs of disease during wet seasons.',
            'Ensure proper crop rotation.'
        ],
        'Squash Powdery Mildew': [
            'Use fungicides regularly.',
            'Ensure good air circulation by spacing plants properly.',
            'Water plants at the base to avoid wetting leaves.'
        ],
        'Potato Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Monitor for signs of blight during wet conditions.',
            'Ensure well-drained soil to prevent root rot.'
        ],
        'Corn Northern Leaf Blight': [
            'Apply fungicides as needed.',
            'Plant disease-resistant varieties.',
            'Rotate crops to avoid disease buildup in soil.'
        ],
        'Tomato Early Blight': [
            'Use fungicides regularly.',
            'Remove and destroy affected leaves.',
            'Water at the base to avoid wetting foliage.'
        ],
        'Tomato Septoria Leaf Spot': [
            'Apply fungicides promptly.',
            'Remove and destroy infected leaves.',
            'Space plants to improve air circulation.'
        ],
        'Corn Cercospora Leaf Spot': [
            'Use resistant hybrids.',
            'Apply fungicides if the disease is severe.',
            'Maintain proper crop rotation practices.'
        ],
        'Strawberry Leaf Scorch': [
            'Apply fungicides as soon as symptoms appear.',
            'Remove and destroy affected leaves.',
            'Avoid overhead watering to reduce leaf wetness.'
        ],
        'Peach Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Prune regularly to ensure good airflow.',
            'Watch for signs of pests like peach tree borers.'
        ],
        'Apple Scab': [
            'Use fungicides during early leaf development.',
            'Remove and destroy fallen leaves.',
            'Plant disease-resistant apple varieties.'
        ],
        'Tomato Yellow Leaf Curl Virus': [
            'Control whiteflies with insecticides.',
            'Remove and destroy infected plants.',
            'Use reflective mulches to deter whiteflies.'
        ],
        'Tomato Bacterial Spot': [
            'Use copper sprays as a treatment.',
            'Avoid working in wet fields to prevent spread.',
            'Rotate crops to reduce bacterial buildup in the soil.'
        ],
        'Apple Black Rot': [
            'Prune and destroy infected branches.',
            'Apply fungicides during early stages.',
            'Avoid mechanical damage to the tree.'
        ],
        'Blueberry Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Mulch to retain moisture and control weeds.',
            'Prune old canes to encourage new growth.'
        ],
        'Cherry Powdery Mildew': [
            'Apply fungicides early in the season.',
            'Improve air circulation by thinning trees.',
            'Avoid excessive nitrogen fertilization.'
        ],
        'Peach Bacterial Spot': [
            'Use bactericides regularly.',
            'Plant resistant varieties if available.',
            'Prune affected branches to reduce spread.'
        ],
        'Apple Cedar Apple Rust': [
            'Apply fungicides during the growing season. ',
            'Remove cedar trees within a few hundred yards. ',
            'Use resistant apple varieties.'
        ],
        'Tomato Target Spot': [
            'Apply fungicide when symptoms first appear.',
            'Rotate crops annually.',
            'Ensure good air circulation around plants.'
        ],
        'Pepper Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Monitor for signs of bacterial spot and anthracnose.',
            'Water in the morning to reduce humidity.'
        ],
        'Grape Leaf Blight': [
            'Remove infected leaves promptly.',
            'Apply fungicides to prevent further spread.',
            'Prune vines to improve airflow.'
        ],
        'Potato Late Blight': [
            'Use fungicides as soon as symptoms appear.',
            'Plant disease-resistant varieties.',
            'Avoid overhead watering to reduce leaf wetness.'
        ],
        'Tomato Mosaic Virus': [
            'Remove infected plants immediately.',
            'Control aphid vectors to prevent spread.',
            'Disinfect tools after working with infected plants.'
        ],
        'Strawberry Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Monitor for signs of fungal diseases like gray mold.',
            'Avoid overhead watering to prevent leaf wetness.'
        ],
        'Apple Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Prune to remove dead wood and improve air circulation.',
            'Monitor for signs of pests like apple maggots.'
        ],
        'Grape Black Rot': [
            'Prune infected areas as soon as detected.',
            'Apply fungicides regularly during wet seasons.',
            'Ensure proper vineyard sanitation by removing debris.'
        ],
        'Potato Early Blight': [
            'Apply fungicides when symptoms first appear.',
            'Practice crop rotation to reduce disease pressure.',
            'Remove and destroy affected foliage.'
        ],
        'Cherry Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Prune to improve air circulation and sunlight penetration.',
            'Watch for signs of fungal diseases like brown rot.'
        ],
        'Corn Common Rust': [
            'Use fungicides if rust becomes severe.',
            'Plant resistant corn varieties.',
            'Rotate crops to reduce rust spores in the soil.'
        ],
        'Grape Esca (Black Measles)': [
            'Avoid overwatering, especially during the growing season.',
            'Prune infected vines and dispose of them properly.',
            'Apply fungicides if the disease is severe.'
        ],
        'Raspberry Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Prune old canes to encourage new growth.',
            'Monitor for signs of cane blight and other diseases.'
        ],
        'Tomato Leaf Mold': [
            'Improve air circulation by spacing plants properly.',
            'Apply fungicides as soon as symptoms appear.',
            'Avoid overhead watering to keep leaves dry.'
        ],
        'Tomato Spider Mites': [
            'Use miticides to control infestations.',
            'Increase humidity to reduce mite activity.',
            'Spray plants with water to dislodge mites.'
        ],
        'Pepper Bacterial Spot': [
            'Use copper-based sprays as a treatment.',
            'Rotate crops to prevent reinfection.',
            'Avoid working in wet fields to reduce spread.'
        ],
        'Corn Healthy': [
            'Your plant is healthy, keep maintaining it!',
            'Monitor for signs of leaf blights or rust.',
            'Ensure proper fertilization and irrigation practices.'
        ]
    }

    return recommendations.get(disease, ["No recommendation available."])


if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True)

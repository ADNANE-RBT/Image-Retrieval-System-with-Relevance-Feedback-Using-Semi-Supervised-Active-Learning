import os
import datetime
from pymongo import MongoClient
from PIL import Image  

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "PhotoMagicDB"
COLLECTION_NAME = "Images"

# Path to the dataset folder
DATASET_FOLDER = ".\\RSSCN7-master"  # Adjust this path if needed

def connect_to_mongo(uri, db_name, collection_name):
    """Connect to MongoDB and return the collection."""
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection

def get_image_dimensions(image_path):
    """Retrieve image dimensions (width, height) using PIL."""
    try:
        with Image.open(image_path) as img:
            return {"width": img.width, "height": img.height}
    except Exception as e:
        print(f"Error reading image dimensions for {image_path}: {e}")
        return {"width": 0, "height": 0}

def process_and_save_images(dataset_folder, collection):
    """Process dataset folder and save the data to MongoDB."""
    for category in os.listdir(dataset_folder):
        category_path = os.path.join(dataset_folder, category)
        
        # Ensure the current item is a directory (category)
        if os.path.isdir(category_path):
            for image_file in os.listdir(category_path):
                image_path = os.path.join(category_path, image_file)
                
                # Ensure the current item is a file (image)
                if os.path.isfile(image_path):
                    try:
                        # Get file size in bytes
                        size = os.path.getsize(image_path)

                        # Get image dimensions
                        dimensions = get_image_dimensions(image_path)

                        # Prepare the document to insert into MongoDB
                        document = {
                            "filename": image_file,
                            "path": image_path,
                            "size": size,
                            "createdAt": datetime.datetime.now(),
                            "dimensions": dimensions,
                            "category": category
                        }

                        # Insert the document into MongoDB
                        collection.insert_one(document)
                        print(f"Inserted: {document}")

                    except Exception as e:
                        print(f"Error processing file {image_path}: {e}")

if __name__ == "__main__":
    # Connect to the MongoDB collection
    collection = connect_to_mongo(MONGO_URI, DB_NAME, COLLECTION_NAME)
    
    # Process the dataset folder and save data to MongoDB
    process_and_save_images(DATASET_FOLDER, collection)

    print("Dataset successfully imported to MongoDB.")

import base64
import requests
import json
import os
import chromadb
import uuid

class ImageProcessor:

    def __init__(self, chroma_collection_name='chroma_collection'):
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        self.chroma_collection_name = chroma_collection_name
        self.image_folder_path = None

    def set_folder_path(self, image_folder_path):
        self.image_folder_path = image_folder_path

    def get_image_paths(self):
        for root, dirs, files in os.walk(self.image_folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in self.image_extensions:
                    yield os.path.join(root, file)

    def get_collection(self):
        client = chromadb.PersistentClient('vectorstore')
        collection = client.get_or_create_collection(name=self.chroma_collection_name)
        return collection
    
    def delete_collection(self):
        client = chromadb.PersistentClient('vectorstore')
        collection = client.get_or_create_collection(name=self.chroma_collection_name)
        collection.delete()

    def load_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        return image_base64

    def describe_image(self, image_base64):

        payload = {
            'model': 'llava',
            'prompt': 'Describe this image',
            'stream': False,
            'images': [image_base64]
        }

        url = 'http://localhost:11434/api/generate'

        response = requests.post(url, data=json.dumps(payload)).json()

        return response['response']

    def process_images(self):

        collection = self.get_collection()
        
        for image_path in self.get_image_paths():

            image_base64 = self.load_image(image_path)
            response = self.describe_image(image_base64)

            collection.add(
                documents=[response],
                ids=[str(uuid.uuid4())],
                metadatas={'image_paths': image_path}
            )

    def query_collection(self, query, n_results):
        collection = self.get_collection()
        results = collection.query(query_texts=[query], n_results=n_results).get('metadatas', {})
        return results
    
if __name__ == '__main__':
    IMAGE_FOLDER_PATH = os.path.join(os.path.dirname(__file__), 'resources')
    image_processor = ImageProcessor(IMAGE_FOLDER_PATH, 'chroma_collection')
    image_processor.process_images()
    results = image_processor.query_collection('trousers', 2)
    print(results)
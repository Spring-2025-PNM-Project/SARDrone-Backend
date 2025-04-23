import os
import asyncio
from app.services.classification import ClassificationModel

async def test_images(folder_path, delay=5):
   
    model = ClassificationModel()
    
    print("\n------------------------------------------------")
    print(f"Testing images in folder: {folder_path}\n")
    print("------------------------------------------------\n")

    images = [f for f in os.listdir(folder_path)]

    for image in images:
        image_path = os.path.join(folder_path, image)
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            result = await model.generate(image_data)
            score = result.get("score", 0)

            if "no_human" in folder_path:
                assert score < 10, f"Image {image} was misclassified. Expected score: < 0, Got: {score} \n"
            elif "yes_human" in folder_path:
                assert score > 90, f"Image {image} was misclassified. Expected score > 90, Got: {score} \n"

        except AssertionError as e:
            print(f"Assertion error for image {image}: {e}")
        except Exception as e:
            print(f"Error processing image {image}: {e}")

        await asyncio.sleep(delay)
        print(f"Processed image: {image} + Score: {score}\n")
        
    print("Successfully processed all images in folder:", folder_path)

async def main():

    no_human = "images/no_human"
    yes_human = "images/yes_human"
  
    await test_images(no_human, delay=5)
    await test_images(yes_human,delay=5)

if __name__ == "__main__":
    asyncio.run(main())
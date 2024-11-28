import os
from pinatapy import PinataPy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PINATA_API_KEY = os.getenv('PINATA_API_KEY')
PINATA_SECRET_API_KEY = os.getenv('PINATA_API_SECRET')

# Connect to Pinata
pinata = PinataPy(PINATA_API_KEY, PINATA_SECRET_API_KEY)

IPFS_PUBLIC_GATEWAY = "https://gateway.pinata.cloud/ipfs/{CID}"


class IPFSHelper:
    """
    Helper class for interacting with Pinata and uploading files to IPFS.
    """

    @staticmethod
    def upload_image_to_ipfs(image, filename="image.png"):
        """
        Uploads an image to IPFS through Pinata.

        Args:
            image (PIL.Image.Image): The image to upload.
            filename (str): Name to assign the uploaded image.

        Returns:
            str: The CID (content identifier) of the uploaded image.
        """
        # Save the image to a temporary file
        temp_file_path = filename
        image.save(temp_file_path, format="PNG")

        try:
            # Upload the image to Pinata
            print(f"Uploading {filename} to Pinata...")
            result = pinata.pin_file_to_ipfs(temp_file_path)
            cid = result['IpfsHash']

            print(f"Image uploaded to Pinata. CID: {cid}")
            return cid
        except Exception as e:
            raise Exception(f"Failed to upload image to Pinata: {e}")
        finally:
            # Delete the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @staticmethod
    def get_ipfs_url(cid):
        """
        Constructs the public URL for accessing an IPFS file.

        Args:
            cid (str): The CID of the content.

        Returns:
            str: The public IPFS URL.
        """
        return IPFS_PUBLIC_GATEWAY.replace("{CID}", cid)

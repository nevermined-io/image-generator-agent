from utils.ipfs_helper import IPFSHelper

def upload_image_and_get_url(image, filename="image.png"):
    """
    Uploads an image to IPFS and returns its public URL.

    Args:
        image (PIL.Image.Image): The image to upload.
        filename (str): The filename to use when uploading the image.

    Returns:
        str: Public URL of the uploaded image on IPFS.
    """
    print(f"Uploading image to IPFS with filename: {filename}")
    cid = IPFSHelper.upload_image_to_ipfs(image, filename)
    return IPFSHelper.get_ipfs_url(cid)

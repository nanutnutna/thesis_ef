import pandas as pd
import aiohttp
import asyncio
import os
import logging
from tqdm.asyncio import tqdm_asyncio



LOG_FILE = "download_images.log"
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()



SAVE_IMG_PATH = r'C:\Users\Nattapot\Desktop\thesis_ef\images'
CSV_PATH = "url_imges.csv"
df = pd.read_csv("url_imges.csv")


async def download_image(session,url,filename):
    try:
        async with session.get(url,) as response:
            if response.status == 200:
                file_path = os.path.join(SAVE_IMG_PATH,f'{filename}.jpg')
                with open(file_path,'wb') as f:
                    f.write(await response.read())
                logger.info(f"[SUCCESS] Downloaded: {url} -> {file_path}")
            else:
                logger.error(f"[ERROR] Failed to download {url} - Status Code: {response.status}")
    except Exception as e:
        logger.exception(f"[ERROR] Exception occurred while downloading {url}: {e}")

async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for row in df.itertuples(index=False):
            if row.License != "-" and pd.notnull(row.img_URL):
                task = download_image(session,url=row.img_URL,filename=row.License)
                tasks.append(task)
        await tqdm_asyncio.gather(*tasks,desc="Downloading Images")


if __name__ == "__main__":
    try:
        logger.info("Starting image download process")
        asyncio.run(main())
        logger.info("Finished images downloaded.")
    except Exception as e:
        logger.critical(f"[CRITICAL] Unexpected error occurred: {e}")

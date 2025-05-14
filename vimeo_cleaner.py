import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm
import vimeo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vimeo_manager.log'),
        logging.StreamHandler()
    ]
)

class VimeoManager:
    def __init__(self):
        self._validate_env_vars()
        self.download_dir = os.getenv('DOWNLOAD_DIR', 'downloads')
        self.per_page = int(os.getenv('PER_PAGE', 100))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.session = self._create_session()
        
        self.vimeo_client = vimeo.VimeoClient(
            token=os.getenv('VIMEO_TOKEN'),
            key=os.getenv('VIMEO_KEY'),
            secret=os.getenv('VIMEO_SECRET'),
            token_type='bearer'
        )
        
        os.makedirs(self.download_dir, exist_ok=True)

    def _validate_env_vars(self):
        """Validate required environment variables"""
        required_vars = ['VIMEO_TOKEN', 'VIMEO_KEY', 'VIMEO_SECRET']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def _create_session(self) -> requests.Session:
        """Create configured requests session with retries"""
        session = requests.Session()
        retries = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def _get_videos(self, page: int) -> Optional[List[Dict]]:
        """Fetch videos from Vimeo API with error handling"""
        try:
            response = self.vimeo_client.get(
                '/me/videos',
                params={
                    'per_page': self.per_page,
                    'page': page,
                    'sort': 'date',
                    'direction': 'asc'
                }
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logging.error(f"Error fetching page {page}: {str(e)}")
            return None

    def _get_download_link(self, video: Dict) -> Optional[str]:
        """Safely extract download link from video data"""
        try:
            return video['download'][0]['link']
        except (KeyError, IndexError):
            logging.warning(f"No download link found for video {video.get('uri', 'unknown')}")
            return None

    def download_video(self, download_link: str, video_name: str) -> bool:
        """Download video with progress tracking and retries"""
        file_path = os.path.join(self.download_dir, f"{video_name}.mp4")
        
        if os.path.exists(file_path):
            logging.info(f"Skipping existing file: {video_name}")
            return True

        try:
            with self.session.get(download_link, stream=True, timeout=30) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))

                with open(file_path, 'wb') as f, tqdm(
                    desc=video_name,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as progress:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))
            return True
        except Exception as e:
            logging.error(f"Download failed for {video_name}: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return False

    def delete_video(self, video_uri: str) -> bool:
        """Delete video from Vimeo with confirmation"""
        try:
            response = self.vimeo_client.delete(video_uri)
            if response.status_code == 204:
                logging.info(f"Successfully deleted: {video_uri}")
                return True
            logging.warning(f"Failed to delete {video_uri}: Status {response.status_code}")
            return False
        except Exception as e:
            logging.error(f"Delete error for {video_uri}: {str(e)}")
            return False

    def process_videos(self, year: int = 2022):
        """Main processing loop with pagination"""
        page = 1
        processed = 0
        errors = 0

        while True:
            videos = self._get_videos(page)
            if not videos:
                break

            for video in videos:
                try:
                    created_time = datetime.fromisoformat(video['created_time'].replace('Z', '+00:00'))
                    if created_time.year != year:
                        continue

                    video_uri = video['uri']
                    video_name = video.get('name', 'unnamed').replace('/', '_')
                    download_link = self._get_download_link(video)

                    if not download_link:
                        errors += 1
                        continue

                    if self.download_video(download_link, video_name):
                        if self.delete_video(video_uri):
                            processed += 1
                        else:
                            errors += 1
                    else:
                        errors += 1

                except Exception as e:
                    logging.error(f"Error processing video: {str(e)}")
                    errors += 1

            page += 1

        logging.info(f"\nProcessing complete!\nSuccess: {processed}\nErrors: {errors}")

if __name__ == '__main__':
    try:
        manager = VimeoManager()
        manager.process_videos(year=2022)
    except Exception as e:
        logging.error(f"Critical error: {str(e)}", exc_info=True)

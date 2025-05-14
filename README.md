# Vimeo-Cleaner
Saves your Vimeo storage by downloading it in an external hard drive, or ssd, or in a folder that you want. I created this code to save up space of the Vimeo cloud storage of a company and they could download in an external HDD what they wouldn't use frequently.

Vimeo Video Manager
A Python tool for automated Vimeo video management (download + deletion) with enhanced security and reliability

Key Features:
🔐 Secure Credential Management - Uses .env files to protect API credentials
📥 Bulk Download - Download multiple Vimeo videos with progress tracking
🗑️ Post-Download Cleanup - Auto-delete videos after successful download
📅 Year Filter - Target videos from specific years (default: 2022)
📊 Detailed Logging - Comprehensive error tracking and success reporting

Use Cases:

Archive old video content from Vimeo

Automate video library cleanup

Bulk backup workflows

Tech Stack:

Python 3.8+

Vimeo API Integration

Requests with retry logic

Progress bars via TQDM

Setup:

bash:
# 1. Clone repo
git clone https://github.com/[your-username]/vimeo-video-manager.git

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env file
cp .env.example .env
Configuration (.env):

ini

VIMEO_TOKEN=your_vimeo_token

VIMEO_KEY=your_vimeo_key

VIMEO_SECRET=your_vimeo_secret

DOWNLOAD_DIR=/path/to/save/videos


Usage:

bash:
python vimeo_manager.py

⚠️ Important:

Test with non-critical videos first

Deletion is permanent - use caution!

Review Vimeo API rate limits

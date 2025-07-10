# MIT License
# Copyright (c) 2025 Su Jiayi <sujiayi2003@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import json
import yaml
import copy
import shutil
import logging
import hashlib
import argparse
import requests
import subprocess

from rich import print
from rich.logging import RichHandler

from tqdm import tqdm
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from multiprocessing import Pool, cpu_count

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)
logger = logging.getLogger("rich")


@dataclass
class NavItem:
    name: str = ''
    path: str = ''
    blank: bool = False

@dataclass
class PostItem:
    title: str = ''
    path: str = ''
    date: str = ''
    year: str = ''
    month: str = ''
    day: str = ''
    weekday: str = ''
    full_date: str = ''
    abstract: str = ''

@dataclass
class CategoryItem:
    title: str = ''
    path: str = ''

@dataclass
class PostHistoryItem:
    datetime: str = ''
    hash: str = ''

@dataclass
class PageData:
    lang: str = "en"
    google_analysis_id: Optional[str] = None
    site_title: str = ''

    keywords: List[str] = field(default_factory=list)
    description: str = ''

    header_path: str = ''
    header_alt: str = ''
    header_desc: str = ''

    nav_list: List[NavItem] = field(default_factory=list)
    current_page: str = ''  # Used to identify the current page (posts, archive, category, about)
    author: str = ''  # Author information
    
    is_post_page: bool = False
    post_content: str = ''
    post_title: str = ''
    post_source_path: str = ''
    post_last_updated: str = ''
    post_word_count: int = 0
    post_reading_time: int = 0
    post_history: List[PostHistoryItem] = field(default_factory=list)
    post_pdf_path: str = ''
    post_formal_logs: str = ''

    is_category_page: bool = False
    category_posts: List[PostItem] = field(default_factory=list)
    category_name: str = ''

    is_category_total_page: bool = False
    category_list: List[CategoryItem] = field(default_factory=list)

    is_post_total_page: bool = False
    post_list: List[PostItem] = field(default_factory=list)

    is_archive_page: bool = False
    archive_post_list: List[PostItem] = field(default_factory=list)

    is_about_page: bool = False
    about_page_content: str = ''

    footer: str = ''


class Utils:
    @classmethod
    def hash_str(cls, text: str):
        hash_value = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return hash_value

    @classmethod
    def get_file_modify_time(cls, file_path: Path):
        return file_path.stat().st_mtime
    
    @classmethod
    def get_file_create_time(cls, file_path: Path):
        return file_path.stat().st_ctime
    
    @classmethod
    def get_str_datetime(cls, timestamp: float):
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def cut_to_lastn_line(cls, text: str, n: int=10):
        lines = text.split('\n')
        return '\n'.join(lines[-n:])
    
    @classmethod
    def count_words(cls, text: str) -> int:
        """Count words in text, supporting mixed Chinese and English"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove inline code
        text = re.sub(r'`[^`]*`', '', text)
        # Remove links
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
        # Remove math formulas
        text = re.sub(r'\$\$[\s\S]*?\$\$', '', text)
        text = re.sub(r'\$[^$]*\$', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Count Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # Count English words
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        
        return chinese_chars + english_words
    
    @classmethod
    def estimate_reading_time(cls, word_count: int) -> int:
        """Estimate reading time (in minutes) based on 200-250 words per minute reading speed"""
        return max(1, round(word_count / 150))
    
    @classmethod
    def _is_chinese(cls, char: str) -> bool:
        """Check if character is Chinese"""
        return '\u4e00' <= char <= '\u9fff'
    
    @classmethod
    def generate_abstract(cls, content: str, title: str = "", config: dict = None) -> str:
        """Generate article abstract using AI model, with fallback to simple abstract"""
        # Get max_chars from config, default to 200
        max_chars = 200
        if config and config.get('ai_abstract'):
            max_chars = config['ai_abstract'].get('max_chars', 200)

        # First try to use DeepSeek API
        try:
            deepseek_abstract = cls._generate_deepseek_abstract(content, title, max_chars)
            if deepseek_abstract:
                return deepseek_abstract
        except Exception as e:
            logging.warning("DeepSeek API call failed, falling back to simple abstract generation: %s", str(e))

        # If DeepSeek API fails, fallback to simple abstract
        return cls._generate_simple_abstract(content, max_chars)
    
    @classmethod
    def _generate_deepseek_abstract(cls, content: str, title: str = "", max_chars: int = 400) -> Optional[str]:
        """Generate article abstract using DeepSeek API"""
        import re
        
        # Read DeepSeek API key
        try:
            with open('deepseek_key.txt', 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
        except Exception as e:
            logging.warning("Failed to read DeepSeek API key: %s", str(e))
            return None
            
        clean_content = content.strip()
        
        if not clean_content:
            return None
            
        # If content is too long, truncate to first 1000 characters
        if len(clean_content) > 1000:
            clean_content = clean_content[:1000]

        chinese_word = len(re.findall(r'[\u4e00-\u9fff]', clean_content))
        english_word = len(re.findall(r'\b[a-zA-Z]+\b', clean_content))
        total_word = chinese_word + english_word
        language_of_article = "Chinese" if (chinese_word / total_word) > 0.3 else "English"
        
        # Prepare request data
        prompt = f"""Please generate a concise summary for the following article with these requirements:
1. Summary length should not exceed {max_chars} characters
2. Highlight the core content and main points of the article
3. Use clear and concise language for readers to quickly understand the article
4. The summary should be complete sentences, not just keywords
5. The language of the summary should be {language_of_article}.

Article title: {title}

Article content:
{clean_content}

Please generate the summary:"""
        
        # Call DeepSeek API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a professional article summarization assistant, skilled at extracting core content from articles and generating concise summaries."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "max_tokens": max_chars * 2,  # Give some buffer
            "temperature": 0.7
        }
        
        try:
            # add cache
            cache_path = Path('cache')
            request_hash = Utils.hash_str(json.dumps(payload))
            cache_file = cache_path / f'{request_hash}.abstract.txt'
            if cache_file.exists():
                return cache_file.read_text()
            
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
             
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and len(result['choices']) > 0:
                    abstract = result['choices'][0]['message']['content'].strip()
                    
                    # If abstract is too long, truncate to appropriate length
                    if len(abstract) > max_chars:
                        # Try to truncate by sentences
                        sentences = re.split(r'[。！？.!?]\s*', abstract)
                        truncated_abstract = ""
                        for sentence in sentences:
                            if len(truncated_abstract + sentence) < max_chars - 3:
                                truncated_abstract += sentence + "。"
                            else:
                                break
                        abstract = truncated_abstract.strip() if truncated_abstract else abstract[:max_chars-3] + "..."
                    
                    cache_file.write_text(abstract)
                    logging.info("DeepSeek API successfully generated abstract")
                    return abstract
                else:
                    logging.warning("DeepSeek API response format error: %s", result)
                    return None
            else:
                logging.warning("DeepSeek API request failed: %s - %s", response.status_code, response.text)
                return None
                
        except Exception as e:
            logging.warning("DeepSeek API request exception: %s", str(e))
            return None
    
    @classmethod
    def _generate_simple_abstract(cls, content: str, max_chars: int = 200) -> str:
        """Simple abstract generation method, as fallback for AI methods"""
        import re
        
        # Remove markdown syntax
        content = re.sub(r'---.*?---', '', content, flags=re.DOTALL)  # Remove YAML front matter
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # Remove code blocks
        content = re.sub(r'`[^`]*`', '', content)  # Remove inline code
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)  # Remove images
        content = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', content)  # Remove links, keep text
        content = re.sub(r'#{1,6}\s*', '', content)  # Remove heading markers
        content = re.sub(r'[*_]{1,2}([^*_]*)[*_]{1,2}', r'\1', content)  # Remove bold/italic
        content = re.sub(r'<!-- more -->', '', content)  # Remove more markers
        content = re.sub(r'\n+', ' ', content)  # Replace newlines with spaces
        content = re.sub(r'\s+', ' ', content)  # Merge multiple spaces
        content = content.strip()
        
        if not content:
            return "No content available."
        
        # Split by sentences, take first few
        sentences = re.split(r'[。！？.!?]\s*', content)
        abstract = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(abstract + sentence) < max_chars - 3:
                abstract += sentence + "。"
            else:
                break
        
        if not abstract:
            # If no suitable sentences, directly truncate
            abstract = content[:max_chars-3] + "..."
        
        return abstract.strip()
    
    @classmethod
    def filter_build_log(cls, log_content: str) -> str:
        """Filter path information in build logs"""
        import re
        
        if not log_content:
            return log_content
            
        # Only replace path information, keep all other content
        filtered_content = log_content
        
        # Replace absolute paths, keep file names
        # Unix-style paths: /path/to/file.ext -> .../file.ext
        filtered_content = re.sub(r'/[/\w\-\.\s]*?([^/\s]+\.(tex|html|md|css|js|py|yaml|yml|sty|cls|cfg|def|fd|aux|pdf|log))(?=\s|$|[),.])', r'.../\1', filtered_content)
        
        # Windows-style paths: C:\path\to\file.ext -> ...\file.ext  
        filtered_content = re.sub(r'[A-Z]:[/\\][/\\w\-\.\s]*?([^/\\s]+\.(tex|html|md|css|js|py|yaml|yml|sty|cls|cfg|def|fd|aux|pdf|log))(?=\s|$|[),.])', r'...\\\\1', filtered_content)
        
        # Replace user directory paths
        filtered_content = re.sub(r'/home/[^/\s]+', '.../[user]', filtered_content)
        filtered_content = re.sub(r'C:\\Users\\[^\\s]+', '...\\[user]', filtered_content)
        
        # Replace temporary directory paths
        filtered_content = re.sub(r'/tmp/[^\s]*', '.../[temp]', filtered_content)
        filtered_content = re.sub(r'C:\\Temp\\[^\s]*', '...\\[temp]', filtered_content)
        
        # Replace system package paths
        filtered_content = re.sub(r'/usr/share/[^\s]*', '.../[system]', filtered_content)
        
        # Replace complete path information in parentheses, but keep file names
        filtered_content = re.sub(r'\(/[^)]*?/([^/)]+\.(sty|cls|cfg|def|fd|tex))\)', r'(.../\1)', filtered_content)
        
        # Add filter explanation header
        header = """Build Log - Filtered
================================================

📋 Information:
• Path information has been filtered for privacy protection
• File names are preserved for debugging purposes  
• All build status and error messages are kept intact

🔍 Filter Rules:
• /absolute/path/file.ext → .../file.ext
• /home/username → .../[user]
• /tmp/files → .../[temp]
• /usr/share/packages → .../[system]

================================================

"""
        
        return header + filtered_content

class GenerateHandler:
    pandoc_html_template:str = "$body$"

    @classmethod
    def filter_special_tag(cls, text: str) -> str:
        cleaned = re.sub(r"{%.*?%}", "\n", text, flags=re.DOTALL)
        return cleaned.strip()

    @classmethod 
    def render_mkd_file_to_html(cls, config, meta_data, content: str, file_id: str):
        if not file_id: file_id = Utils.hash_str(content)

        cache_path: Path = config['cache_path']
        
        author = config['author']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        meta_data.update({
            'title': meta_data.get('title', ''),
            'author': author,
        })
        if not meta_data.get('date'):
            meta_data['date'] = date
        
        mk_path = cache_path / f'{file_id}.md'
        mk_path.write_text('---\n' + yaml.dump(meta_data, allow_unicode=True) + '\n---\n' + content)

        html_path = cache_path / f'{file_id}.md.html'
        template_path = config['pandoc_html_template_path']

        subp = subprocess.Popen(cmd := [
                "pandoc",
                "-s", mk_path.as_posix(),
                "--filter", "pandoc-crossref",
                "--filter", "pandoc-katex",
                '--template=' + template_path.as_posix(), 
                '-o', html_path.as_posix(),
                '--metadata',
                '--verbose',
                '--highlight-style=tango'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = subp.communicate()
        (cache_path / f'{file_id}.stdout.txt').write_text(stdout)
        (cache_path / f'{file_id}.stderr.txt').write_text(stderr)

        if subp.returncode != 0:
            logging.warning("%s compile failed, pandoc log following.", file_id)
            logging.warning("stdout %s %s.", file_id, Utils.cut_to_lastn_line(stdout, 10))
            logging.warning("stderr %s %s.", file_id, Utils.cut_to_lastn_line(stderr, 10))
            return None
        
        formal_logs = f"CMD: {cmd}\nSTDOUT: {stdout}\nSTDERR: {stderr}"

        html = html_path.read_text()
        return html, formal_logs
    
    @classmethod
    def render_mkd_file_to_pdf(cls, config, meta_data, content: str, file_id: str):
        if not file_id: file_id = Utils.hash_str(content)
        hash_cut = Utils.hash_str(content)[:10]
        file_id += "_" + hash_cut

        cache_path: Path = config['cache_path'] 

        pdf_path = cache_path / f'{hash_cut}.pdf'
        if pdf_path.exists() and (cache_path / f'{hash_cut}.formal_logs.txt').exists():
            return pdf_path.read_bytes(), (cache_path / f'{hash_cut}.formal_logs.txt').read_text()

        author = config['author']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logging.info("Render %s to pdf.", file_id)

        meta_data.update({
            'title': meta_data['title'],
            'author': author,
            'linestretch': 1.3,
            'CJKmainfont': 'AR PL UKai CN',
            'mainfont': 'Latin Modern Roman',
            'geometry': [
                'a4paper',
                'margin=2cm'
            ]
        })
        if not meta_data.get('date'):
            meta_data['date'] = date

        yaml_content = yaml.dump(meta_data, allow_unicode=True)

        mk_path = cache_path / f'{hash_cut}.pdf.md'
        mk_path.write_text('---\n' + yaml_content + '\n---\n' + content)


        subp = subprocess.Popen(cmd := [
                "pandoc",
                "-s", mk_path.as_posix(),
                "-o", pdf_path.as_posix(),
                # "-V", f"title='{title}'",
                # "-V", f"author='{author}'",
                # "-V", "linestretch=1.5",
                # "-V", f"date='{date}'",
                # "-V", "CJKmainfont='Noto Serif CJK SC'",
                # "-V", "mainfont='Noto Serif'",
                # "--template=static/pandoc.template.tex",
                "-H", "static/pandoc.header.tex",
                "--pdf-engine=xelatex",
                "--verbose"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info("Running command: %s", ' '.join(cmd))
        stdout, stderr = subp.communicate()
        (cache_path / f'{hash_cut}.stdout.txt').write_text(stdout)
        (cache_path / f'{hash_cut}.stderr.txt').write_text(stderr)

        if subp.returncode != 0:
            logging.warning("%s compile failed, pandoc log following.", file_id)
            logging.warning("stdout %s %s.", file_id, Utils.cut_to_lastn_line(stdout, 10))
            logging.warning("stderr %s %s.", file_id, Utils.cut_to_lastn_line(stderr, 10))
            return None

        formal_logs = f"CMD: {cmd}\nSTDOUT: {stdout}\nSTDERR: {stderr}"
        (cache_path / f'{hash_cut}.formal_logs.txt').write_text(formal_logs)
        pdf = pdf_path.read_bytes()
        return pdf, formal_logs
    
    @classmethod
    def render_btex_file_to_pdf(cls, env, config, meta_data, content: str, file_id: str):
        # print(content)
        if not file_id: file_id = Utils.hash_str(content)

        file_id += "_" + Utils.hash_str(content)[:10]

        cache_path: Path = config['cache_path']

        pdf_path = cache_path / f'{file_id}.pdf'
        if pdf_path.exists() and (cache_path / f'{file_id}.formal_logs.txt').exists():
            return pdf_path.read_bytes(), (cache_path / f'{file_id}.formal_logs.txt').read_text()
        
        logging.info("Render %s to pdf.", file_id)

        preamble = ''
        if meta_data.get('preamble'):
            try:
                with open('src/_common/' + meta_data.get('preamble'), 'r', encoding='utf-8') as f:
                    preamble = f.read()
            except Exception as e:
                logging.warning("Error reading preamble of %s, msg: %s.", file_id, str(e))
                return None

        tex_path = cache_path / f'{file_id}.tex'
        tex_path.write_text(content)

        title = meta_data['title']
        author = config['author']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subp = subprocess.Popen(cmd := [
                "pandoc",
                tex_path.as_posix(),
                "-o", pdf_path.as_posix(),
                "-V", f'title="{title}"',
                "-V", f'author="{author}"',
                "-V", "linestretch=1.5",
                "-V", "date=" + date,
                "-V", 'CJKmainfont="Noto Serif CJK SC"',
                "-V", 'mainfont="Noto Serif"',
                # "--template=static/pandoc.template.tex",
                "-H", "static/pandoc.header.tex",
                "--pdf-engine=xelatex",
                "--verbose"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info("Running command: %s", ' '.join(cmd))
        stdout, stderr = subp.communicate()
        (cache_path / f'{file_id}.stdout.txt').write_text(stdout)
        (cache_path / f'{file_id}.stderr.txt').write_text(stderr)
        
        if subp.returncode != 0:
            logging.warning("%s compile failed, pdflatex log following.", file_id)
            logging.info("stdout %s %s.", file_id, Utils.cut_to_lastn_line(stdout, 10))
            logging.warning("stderr %s %s.", file_id, Utils.cut_to_lastn_line(stderr, 10))
            return None

        formal_logs = f"CMD: {cmd}\nSTDOUT: {stdout}\nSTDERR: {stderr}"
        (cache_path / f'{file_id}.formal_logs.txt').write_text(formal_logs)

        pdf = pdf_path.read_bytes()
        return pdf, formal_logs

    @classmethod 
    def render_btex_file_local_to_html(cls, config, meta_data, content: str, file_id: str):
        if meta_data.get('preamble'):
            try:
                with open('src/_common/' + meta_data.get('preamble'), 'r', encoding='utf-8') as f:
                    preamble = f.read()
            except Exception as e:
                logging.warning("Error reading preamble of %s, msg: %s.", file_id, str(e))
                return None
            content = preamble + '\n' + content

        if not file_id: file_id = Utils.hash_str(content)

        cache_path: Path = config['cache_path']
        btex_path = cache_path / f'{file_id}.btex'
        btex_path.write_text(content)

        html_path = cache_path / f'{file_id}.btex.html'

        subp = subprocess.Popen(cmd := [
                "nodejs",
                "btex/dist/cli.js",
                "-i", btex_path.as_posix(),
                "-o", html_path.as_posix(),
                "--css=false"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = subp.communicate()
        (cache_path / f'{file_id}.stdout.txt').write_text(stdout)
        (cache_path / f'{file_id}.stderr.txt').write_text(stderr)

        if subp.returncode != 0:
            logging.warning("%s compile failed, btex log following.", file_id)
            if stdout: logging.info("stdout %s %s", file_id, Utils.cut_to_lastn_line(stdout, 10))
            logging.info("stdout %s %s", file_id, Utils.cut_to_lastn_line(stdout, 10))
            logging.warning("stderr %s %s", file_id, Utils.cut_to_lastn_line(stderr, 10))
            return None
        
        formal_logs = f"CMD: {cmd}\nSTDOUT: {stdout}\nSTDERR: {stderr}"
        html = html_path.read_text()
        return html, formal_logs
    
    @classmethod
    def render_btex_file_remote(cls, config, meta_data, content: str, file_id: str):
        btex_server_host = config['btex_server_host']
        btex_server_post = config['btex_server_port']
        if meta_data.get('preamble'):
            preamble = ''
            try:
                with open('src/_common/' + meta_data.get('preamble'), 'r') as f:
                    preamble = f.read()
            except Exception as e:
                logging.warning("Error reading preamble of %s, msg: %s.", file_id, str(e))
            content = preamble + '\n' + content
        try:
            resp = requests.post(f"http://{btex_server_host}:{btex_server_post}", 
                                headers={"Content-Type": "application/json"},
                                json={"code": content})
        except Exception as e:
            logging.warning("Error calling with btex server: %s", str(e))
            return None
        if resp.status_code != 200:
            logging.warning("Error response from btex server: %s, response: %s.", resp.status_code, resp.text)
            return None
        
        result = resp.json()
        if not result['html']:
            logging.warning("Error compile %s: \nerror: %s \nwarn: %s.", file_id, '\n'.join(result['errors']), '\n'.join(result['warnings']))
            return None

        return result['html']
    
    @classmethod
    def split_meta_and_content(cls, file_name, file_content):
        try:
            if not file_content.startswith('---'):
                raise ValueError("markdown must startswith --- for meta info.")
            
            meta_data = file_content.split('---')[1]
            pure_content = '---'.join(file_content.split('---')[2:])

            return (yaml.safe_load(meta_data), pure_content)
        except Exception as e:
            logging.warning("Parse meta info error %s: [%s] %s, skip.", file_name, type(e), str(e))
            return None
    
    @classmethod
    def get_history_info(cls, config):
        history_path = Path('db.json')
        if not history_path.exists():
            history_path.write_text('{}')

        with open(history_path, 'r', encoding='utf-8') as f:
            history_info = json.load(f)
        return history_info
    
    @classmethod
    def update_history_info(cls, config, history_info):
        history_path = Path('db.json')
        history_path.write_text(json.dumps(history_info, indent=4))
        return history_info

    @classmethod
    def main(cls, args):
        if not args.config.exists():
            logging.error("%s does not exist!", args.config)
            return 
        else:
            with open(args.config, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        
        env = Environment(loader=FileSystemLoader("static"), autoescape=True)
        layout_template = env.get_template("layout.html")

        
        # set up temp folder.
        cache_path = Path('cache')
        cache_path.mkdir(exist_ok=True)
        config['cache_path'] = cache_path

        html_path = Path('html')
        shutil.rmtree(html_path, ignore_errors=True)
        html_path.mkdir()

        pdf_path = Path('pdf')
        shutil.rmtree(pdf_path, ignore_errors=True)
        pdf_path.mkdir()

        pandoc_html_template_path = cache_path / "pandoc_html_template.html"
        pandoc_html_template_path.write_text(cls.pandoc_html_template)
        config['pandoc_html_template_path'] = pandoc_html_template_path

        history_info = cls.get_history_info(config)

        template_page_data = PageData(site_title=config['site_title'],
                                      keywords=config['basic_keywords'] or [],
                                      description=config['basic_description'] or '',
                                      header_path=config['header_path'],
                                      header_alt=config['header_alt'],
                                      header_desc=config['header_desc'],
                                      footer=config['footer'],
                                      google_analysis_id=config['google_analysis_id'],
                                      author=config['author'])
        template_page_data.nav_list = [
            NavItem(name='Posts', path='./_post.html', blank=False),
            NavItem(name='Archive', path='./_archive.html', blank=False),
            NavItem(name='Category', path='./_category.html', blank=False),
            NavItem(name='About', path='./_about.html', blank=False)
        ]

        category_path_list = list(filter(lambda x : not x.stem.startswith('_'), (Path('src').glob('*'))))

        post_list = [src_post_path 
                    for category_path in category_path_list
                    for src_post_path in category_path.glob('*')]
        
        print(post_list)

        post_dict_list = []
        category_path_to_name = {}

        pool = Pool(processes=int(cpu_count() * 0.7))

        for post_path in tqdm(post_list, desc="Compile post"):
            file_content = post_path.read_text()
            file_content_hash = Utils.hash_str(file_content)
            file_id = (post_path.parent.stem + '_' + post_path.stem)

            result = cls.split_meta_and_content(post_path, file_content)
            if result is None:
                logging.error("Error parse meta info of %s, skip.", post_path)
                continue
            meta_data, pure_content = result

            if meta_data.get('skip', False):
                logging.info("Skip %s.", post_path)
                continue

            if not history_info.get(file_id):
                history_info[file_id] = []
            
            if len(history_info[file_id]) == 0:
                history_info[file_id].append({
                    'datetime': meta_data.get('date', datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    'hash': file_content_hash,
                })
            elif history_info[file_id][-1]['hash'] != file_content_hash:
                history_info[file_id].append({
                    'datetime': Utils.get_str_datetime(Utils.get_file_modify_time(post_path)),
                    'hash': file_content_hash,
                })

            if post_path.suffix == '.md':
                pure_content = cls.filter_special_tag(pure_content)
                
                # render html
                result = cls.render_mkd_file_to_html(config, meta_data, pure_content, file_id)
                if result is None: 
                    logging.warning("Error response from pandoc when compile %s.", file_id)
                    continue
                html, html_formal_logs = result

                # process category index post.
                is_category_index_post = (post_path.stem == 'index')
                if is_category_index_post:
                    if meta_data.get('category_name'):
                        category_path_to_name[post_path.parent.stem] = meta_data.get('category_name')
                    else:
                        logging.error("Not found `category_name` in the meta info of %s", post_path)
                        return 
                else:
                    if not meta_data.get('title'):
                        logging.warning('Not found `title` in the meta info of %s, skip', post_path)
                        continue
                
                # render pdf
                cur_pdf_path = None; pdf_formal_logs = None
                if not is_category_index_post:
                    # print("call #1", post_path)
                    result = cls.render_mkd_file_to_pdf(config, meta_data, pure_content, file_id)
                    if result is None: 
                        logging.warning("Error compile %s to pdf.", file_id)
                        # logging.warning(pdf_formal_logs)
                    else:
                        pdf, pdf_formal_logs = result
                        cur_pdf_path = pdf_path / (post_path.parent.stem + '_' + post_path.stem + '.pdf')
                        with open(cur_pdf_path, 'wb') as f:
                            f.write(pdf)
                
                post_dict_list.append({
                    'path': post_path,
                    'meta_data': meta_data,
                    'title': meta_data.get('title'),
                    'category_name': meta_data.get('category_name'),
                    'is_category_index_post': is_category_index_post,
                    'html': html,
                    'file_content': file_content,
                    'file_hash': file_content_hash,
                    'pdf_path': cur_pdf_path,
                    'abstract': pool.apply_async(Utils.generate_abstract, (file_content, meta_data.get('title'), config)),
                    'formal_logs': 'html log:\n' + str(html_formal_logs) + '\n' + '=' * 100 + '\npdf log:\n' + str(pdf_formal_logs)
                })
            elif post_path.suffix == '.btex':
                pure_content = cls.filter_special_tag(pure_content)
                result = cls.render_btex_file_local_to_html(config, meta_data, pure_content, file_id)
                if result is None:
                    logging.warning("Error return when compile from %s.", file_id)
                    continue

                html, html_formal_logs = result

                cur_pdf_path = None; pdf_formal_logs = None
                # print("call #2", post_path)
                result = cls.render_btex_file_to_pdf(env, config, meta_data, pure_content, file_id)
                if result is None: 
                    logging.warning("Error compile %s to pdf.", file_id)
                    # logging.warning(pdf_formal_logs)
                else:
                    pdf, pdf_formal_logs = result
                    cur_pdf_path = pdf_path / (post_path.parent.stem + '_' + post_path.stem + '.pdf')
                    with open(cur_pdf_path, 'wb') as f:
                        f.write(pdf)

                post_dict_list.append({
                    'path': post_path,
                    'meta_data': meta_data,
                    'title': meta_data.get('title'),
                    'category_name': '',
                    'is_category_index_post': False,
                    'html': html,
                    'file_content': file_content,
                    'file_hash': file_content_hash,
                    'pdf_path': cur_pdf_path,
                    'abstract': pool.apply_async(Utils.generate_abstract, (file_content, meta_data.get('title'), config)),
                    'formal_logs': 'html log:\n' + str(html_formal_logs) + '\n' + '=' * 100 + '\npdf log:\n' + str(pdf_formal_logs)
                })
            else:
                logging.warning('skip %s, not suport %s.', post_path, post_path.suffix)
                continue
        
        for post in tqdm(post_dict_list, desc="Generate Abstract"):
            post['abstract'] = post['abstract'].get()
        pool.close()
        pool.join()

        # print(history_info)
        cls.update_history_info(config, history_info)

        # print(post_dict_list)

        # output posts only
        for post in tqdm(list(filter(lambda x : not x['is_category_index_post'], post_dict_list)), desc='Output Post HTML'):
            file_id = (post['path'].parent.stem + '_' + post['path'].stem)
            page_data = copy.deepcopy(template_page_data)
            page_data.post_content = post['html']
            page_data.post_title = post['title']
            page_data.post_source_path = "../" + str(post['path'])
            page_data.is_post_page = True
            
            # Calculate article statistics
            word_count = Utils.count_words(post['file_content'])
            page_data.post_word_count = word_count
            page_data.post_reading_time = Utils.estimate_reading_time(word_count)
            
            # Get last update date
            post_history = history_info.get(file_id, [])
            if post_history:
                page_data.post_last_updated = post_history[-1]['datetime'].split(' ')[0]  # Only date part
            else:
                page_data.post_last_updated = datetime.now().strftime("%Y-%m-%d")
            
            page_data.post_history = post_history
            page_data.post_pdf_path = "../" + str(post['pdf_path']) if post['pdf_path'] else ''
            page_data.post_formal_logs = Utils.filter_build_log(post['formal_logs'])
            html = layout_template.render(asdict(page_data))
            curr_html_path = html_path / (post['path'].parent.stem + '_' + post['path'].stem + '.html')
            curr_html_path.write_text(html)
            post['html_path'] = curr_html_path

        # output category page
        category_path_to_html_path = {}
        for pathname, cate_name in tqdm(list(category_path_to_name.items()), desc="Output Cate HTML"):
            curr_cate_post = list(filter(
                lambda post : (not post['is_category_index_post']) and (post['path'].parent.stem == pathname),
                post_dict_list
            ))
            page_data = copy.deepcopy(template_page_data)
            page_data.category_name = cate_name
            page_data.is_category_page = True
            page_data.category_posts = [
                PostItem(title=post['title'], path='./' + post['html_path'].name, date='', year='', abstract=post['abstract'])
                for post in curr_cate_post
            ]
            html = layout_template.render(asdict(page_data))

            curr_html_path = html_path / (pathname + "_category_index" + '.html')
            curr_html_path.write_text(html)
            category_path_to_html_path[pathname] = curr_html_path
        
        # output category_main page
        page_data = copy.deepcopy(template_page_data)
        page_data.category_list = [
            CategoryItem(title=category_path_to_name[pathname], path='./' + category_path_to_html_path[pathname].name)
            for pathname in list(category_path_to_name.keys())
        ]
        page_data.is_category_total_page = True
        page_data.current_page = "category"
        html = layout_template.render(asdict(page_data))
        curr_html_path = html_path / ('_category.html')
        curr_html_path.write_text(html)
        logging.info("Category Overall Page Generated.")


        # output post_main page
        page_data = copy.deepcopy(template_page_data)
        
        # Create post list with date information and sort by date (newest first)
        post_items = []
        for post in tqdm(list(filter(lambda x : not x['is_category_index_post'], post_dict_list)), desc="Output Post HTML"):
            post_date = post['meta_data'].get('date', '1970-01-01')
            if isinstance(post_date, datetime):
                post_date_str = post_date.strftime('%Y-%m-%d')
                post_year = post_date.strftime('%Y')
                post_month = post_date.strftime('%m')
                post_day = post_date.strftime('%d')
                post_weekday = post_date.strftime('%A')
                post_full_date = post_date.strftime('%B %d, %Y')
            else:
                post_date_str = str(post_date).split(' ')[0] if post_date else '1970-01-01'
                try:
                    date_obj = datetime.strptime(post_date_str, '%Y-%m-%d')
                    post_year = date_obj.strftime('%Y')
                    post_month = date_obj.strftime('%m')
                    post_day = date_obj.strftime('%d')
                    post_weekday = date_obj.strftime('%A')
                    post_full_date = date_obj.strftime('%B %d, %Y')
                except:
                    post_year = post_date_str.split('-')[0] if '-' in post_date_str else '1970'
                    post_month = post_date_str.split('-')[1] if '-' in post_date_str else '01'
                    post_day = post_date_str.split('-')[2] if '-' in post_date_str and len(post_date_str.split('-')) > 2 else '01'
                    post_weekday = 'Unknown'
                    post_full_date = post_date_str
            
            post_items.append(PostItem(
                title=post['title'], 
                path='./' + post['html_path'].name,
                date=post_date_str,
                year=post_year,
                month=post_month,
                day=post_day,
                weekday=post_weekday,
                full_date=post_full_date,
                abstract=post['abstract']
            ))
        
        # Sort posts by date (newest first)
        post_items.sort(key=lambda x: x.date, reverse=True)
        
        page_data.post_list = post_items
        page_data.is_post_total_page = True
        page_data.current_page = "posts"
        html = layout_template.render(asdict(page_data))
        curr_html_path = html_path / ('_post.html')
        curr_html_path.write_text(html)
        logging.info("Posts Overall Page Generated.")

        # output archive page (detailed version of post list)
        page_data = copy.deepcopy(template_page_data)
        page_data.archive_post_list = post_items  # Same post items but for archive template
        page_data.is_archive_page = True
        page_data.current_page = "archive"
        html = layout_template.render(asdict(page_data))
        curr_html_path = html_path / ('_archive.html')
        curr_html_path.write_text(html)
        logging.info("Archive Page Generated.")

        # output about me page.
        about_page_md_path = Path("src/about.md")
        if about_page_md_path.exists():
            result = cls.render_mkd_file_to_html(config, {}, about_page_md_path.read_text(), file_id)
            if result is None:
                logging.warning("Error compile %s to html.", about_page_md_path)
                return
            partial_html, _ = result
            page_data = copy.deepcopy(template_page_data)
            page_data.about_page_content = partial_html
            page_data.is_about_page = True
            page_data.current_page = "about"

            html = layout_template.render(asdict(page_data))
            curr_html_path = html_path / ('_about.html')
            curr_html_path.write_text(html)
            logging.info("About Page Generated.")
        else:
            logging.warning("%s does not exist.", about_page_md_path)

        # Generate index.html redirect page
        index_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0; url=./_post.html">
    <title>Redirecting...</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .redirect-container {
            text-align: center;
            padding: 2rem;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .spinner {
            width: 40px;
            height: 40px;
            margin: 1rem auto;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        h1 {
            margin: 0 0 1rem 0;
            font-size: 1.5rem;
            font-weight: 600;
        }
        p {
            margin: 0;
            opacity: 0.9;
        }
        a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="redirect-container">
        <h1>Welcome to ''' + config['site_title'] + '''</h1>
        <div class="spinner"></div>
        <p>Redirecting to blog posts...</p>
        <p style="margin-top: 1rem; font-size: 0.9rem;">
            If you are not redirected automatically, 
            <a href="./_post.html">click here</a>.
        </p>
    </div>
    
    <script>
        // Backup JavaScript redirect in case meta refresh fails
        setTimeout(function() {
            window.location.href = './_post.html';
        }, 100);
    </script>
</body>
</html>'''
        
        index_html_path = html_path / 'index.html'
        index_html_path.write_text(index_html_content)
        logging.info("Index redirect page generated.")


class CreateCategoryHandler:
    index_md_template: str = '''---
category_name: default_category_name
---

default_category_description

'''

    @classmethod
    def main(cls, args):
        cate_name = args.name

        if cate_name.startswith('_'):
            logging.error("Category name can not be start with _.")
            return

        cate_path = Path(f'src/{cate_name}')
        if cate_path.exists():
            logging.warning("%s already exists! skip.", cate_path)
        else:
            cate_path.mkdir(parents=True)
        
        cate_index_file_path = cate_path / "index.md"
        if cate_index_file_path.exists():
            logging.warning("%s already exists! skip.", cate_index_file_path)
        else:
            cate_index_file_path.write_text(cls.index_md_template)
            logging.info("%s writed, please change the content in it.", cate_index_file_path)

class ClearCacheHandler:
    @classmethod
    def main(cls, args):
        cache_path = Path('cache')
        shutil.rmtree(cache_path, ignore_errors=True)
        cache_path.mkdir()
        logging.info("Cache data cleared.") 

def main():
    logging.info("Hiiiii, this script was made with ❤️  by ShuYuMo (or Jiayi Su)!")

    parser = argparse.ArgumentParser(description="Blog Static File Generator.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # re-Generate static site.
    gen_parser = subparsers.add_parser("generate", aliases=['gen', 'g'], help="re-Generate static site.")
    gen_parser.add_argument("-c", "--config", type=Path, default='./config.yaml', help="site config.")
    gen_parser.set_defaults(func=GenerateHandler.main)

    # Create new category.
    cate_parser = subparsers.add_parser("create_category", aliases=['cc', 'c'], help="create new category.")
    cate_parser.add_argument("-n", "--name", type=str, required=True, help="name of the category.")
    cate_parser.set_defaults(func=CreateCategoryHandler.main)

    # Clear Cache.
    clea_parser = subparsers.add_parser("clean_cache_data", aliases=['cl', 'clean'], help="clean cache data.")
    clea_parser.set_defaults(func=ClearCacheHandler.main)

    args = parser.parse_args()
    args.func(args)

    logging.info("done, Bye!")

if __name__ == '__main__':
    main()
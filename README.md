# Crawler Data



1. Install the dependencies:
```bash
# Debian-based:
sudo apt install wget git python3 python3-venv
# Red Hat-based:
sudo dnf install wget git python3
# Arch-based:
sudo pacman -S wget git python3
```

2. Clone source git:
```bash
git clone https://github.com/hphucngh/crawler-data.git
```
3. Run 
`python3 -m venv venv`
`source venv/bin/activate`
`pip install poetry`
`poetry install`

4. Create crawler 
`scrapy startproject < ex: src> .`
`scrapy genspider example example.com`

5. Install package
`playwright install`

### Run 
`scrapy crawl tapchibitcoin_tapchi -o data.json`
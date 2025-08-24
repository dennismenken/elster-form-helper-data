import requests
from bs4 import BeautifulSoup, Tag, Comment, NavigableString
from bs4 import NavigableString, Comment
import re

current_year = '2022'
current_form = 'kst'

def join_markdown_blocks(lines):
    """Join markdown lines smartly, keeping lists together without blank lines."""
    result = []
    prev_was_list = False

    list_pattern = re.compile(r"^(\d+\.\s|[-*+]\s)")

    for line in lines:
        is_list = bool(list_pattern.match(line))

        if prev_was_list and is_list:
            # Continue list without blank line
            result.append(line)
        elif result:
            # Separate blocks with a blank line
            result.append("")
            result.append(line)
        else:
            result.append(line)

        prev_was_list = is_list

    return "\n".join(result)


def clean_text(element):
    """Cleans and flattens all text inside the element, preserving inline flow without inserting line breaks."""
    # Remove <br> completely
    for br in element.find_all("br"):
        br.decompose()

    # Unwrap inline tags like <abbr>, <span> etc.
    for tag in element.find_all(['abbr', 'span', 'strong', 'b', 'i', 'em']):
        tag.unwrap()

    # Collect text in document order while preserving inline flow
    text_parts = []
    def collect_text(node):
        for child in node.children:
            if isinstance(child, Comment):
                continue
            elif isinstance(child, NavigableString):
                text_parts.append(str(child))
            elif isinstance(child, Tag):
                collect_text(child)

    collect_text(element)

    # Join and normalize whitespace
    return ' '.join(''.join(text_parts).split())


def handle_paragraph(element, heading_level):
    """Handles <p> tags with potentially complex children (divs, toggles, etc.), merging inline text."""
    lines = []
    buffer = []

    def flush_buffer():
        if buffer:
            merged = ' '.join(buffer)
            merged = ' '.join(merged.split())  # Normalize whitespace
            if merged:
                lines.append(merged)
            buffer.clear()

    for child in element.children:
        if isinstance(child, Comment):
            continue
        elif isinstance(child, Tag):
            classes = child.get('class') or []
            if 'toggleBox' in classes or 'global-help__block' in classes:
                flush_buffer()
                lines.extend(process_element(child, heading_level))
            elif child.name.startswith('h'):
                flush_buffer()
                lines.append(f"{'#' * heading_level} {clean_text(child)}")
            elif child.name in ['ul', 'ol']:
                flush_buffer()
                lines.extend(process_element(child, heading_level))
            elif child.name in ['p', 'div']:
                flush_buffer()
                lines.extend(handle_paragraph(child, heading_level))
            else:
                txt = clean_text(child)
                if txt:
                    buffer.append(txt)
        elif isinstance(child, NavigableString):
            stripped = str(child).strip()
            if stripped:
                buffer.append(stripped)

    flush_buffer()
    return lines


def process_toggle(toggle, base_heading):
    lines = []
    base_heading += 1
    head = toggle.select_one('.toggleBox__head .toggleBox__title')
    if head:
        lines.append(f"{'#' * base_heading} {clean_text(head)}")
    content = toggle.select_one('.toggleBox__content')
    if content:
        for child in content.children:
            if isinstance(child, Comment):
                continue
            if isinstance(child, Tag):
                lines.extend(process_element(child, base_heading + 1))  # deeper for inner headings
    return lines

def process_element(element, heading_level):
    lines = []
    if element.name.startswith('h'):
        lines.append(f"{'#' * heading_level} {clean_text(element)}")
    elif element.name == 'p':
        lines.extend(handle_paragraph(element, heading_level))
    elif element.name in ['ul', 'ol']:
        list_items = element.find_all('li', recursive=False)
        for idx, li in enumerate(list_items, 1):
            li_text = clean_text(li)
            if li_text:
                prefix = f"{idx}." if element.name == 'ol' else "-"
                lines.append(f"{prefix} {li_text}")
    elif element.get('class'):
        if 'toggleBox' in element.get('class'):
            lines.extend(process_toggle(element, heading_level))
        elif 'global-help__block' in element.get('class'):
            for sub in element.children:
                if isinstance(sub, Tag):
                    lines.extend(process_element(sub, heading_level + 1))
    return lines

def process_content(main_block):
    lines = []
    base_heading = 2
    for child in main_block.children:
        if isinstance(child, Comment):
            continue
        if isinstance(child, Tag):
            lines.extend(process_element(child, base_heading))
    return lines

# Fetch and parse HTML

elster_urls_dict = {
    'kst': {
        '2020': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_kst_2020',
        '2021': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_kst_2021',
        '2022': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_kst_2022',
        '2023': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_kst_2023',
        '2024': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_kst_2024'
    },
    'gewst': {
        '2020': 'https://www.elster.de/elsterweb/helpGlobal?themaGlobal=help_gewst_ufa_20_2020',
        '2021': 'https://www.elster.de/elsterweb/helpGlobal?themaGlobal=help_gewst_ufa_20_2021',
        '2022': 'https://www.elster.de/elsterweb/helpGlobal?themaGlobal=help_gewst_ufa_20_2022',
        '2023': 'https://www.elster.de/elsterweb/helpGlobal?themaGlobal=help_gewst_ufa_20_2023',
        '2024': 'https://www.elster.de/elsterweb/helpGlobal?themaGlobal=help_gewst_ufa_20_2024'
    },
    'ust': {
        '2020': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_ust_ufa_50_2020',
        '2021': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_ust_ufa_50_2021',
        '2022': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_ust_ufa_50_2022',
        '2023': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_ust_ufa_50_2023',
        '2024': 'https://www.elster.de/eportal/helpGlobal?themaGlobal=help_ust_ufa_50_2024'
    }
}

response = requests.get(elster_urls_dict[current_form][current_year])
soup = BeautifulSoup(response.content, "html.parser")

main_blocks = soup.select("main > div > div > .global-help__block")
if not main_blocks:
    raise ValueError("Keine global-help__block-Elemente gefunden!")

markdown_lines = []
for block in main_blocks:
    markdown_lines.extend(process_content(block))
markdown_output = join_markdown_blocks(markdown_lines)

with open(f"elster_{current_form}{current_year}_help.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)

print(f"Markdown export complete: elster_{current_form}{current_year}_help.md")

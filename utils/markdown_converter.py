#!/usr/bin/env python3
"""
Markdown to HTML Converter for Clinical Documentation
Converts user-friendly Markdown to beautifully styled HTML with custom CSS
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MarkdownToHTMLConverter:
    """Converts Markdown to HTML with clinical-friendly styling."""
    
    def __init__(self, css_path: Optional[Path] = None):
        """Initialize the converter.
        
        Args:
            css_path: Path to custom CSS file. If None, uses default.
        """
        if css_path is None:
            # Default to user_facing styles.css
            css_path = Path(__file__).parent.parent / "docs" / "user_facing" / "styles.css"
        
        self.css_path = css_path
        self.css_content = self._load_css()
    
    def _load_css(self) -> str:
        """Load CSS content from file.
        
        Returns:
            CSS content as string
        """
        if self.css_path.exists():
            with open(self.css_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def convert(self, markdown_text: str, theme: str = "light") -> str:
        """Convert Markdown text to HTML.
        
        Args:
            markdown_text: Markdown content to convert
            theme: Theme name ("light" or "dark")
            
        Returns:
            Complete HTML document with styling
        """
        # Apply conversions in order
        html = markdown_text
        
        # Convert headers
        html = self._convert_headers(html)
        
        # Convert bold and italic
        html = self._convert_emphasis(html)
        
        # Convert lists
        html = self._convert_lists(html)
        
        # Convert code blocks (minimal - remove or simplify)
        html = self._remove_code_blocks(html)
        
        # Convert inline code (simplify)
        html = self._convert_inline_code(html)
        
        # Convert horizontal rules
        html = self._convert_horizontal_rules(html)
        
        # Convert links
        html = self._convert_links(html)
        
        # Convert tables
        html = self._convert_tables(html)
        
        # Convert blockquotes
        html = self._convert_blockquotes(html)
        
        # Convert special callouts
        html = self._convert_callouts(html)
        
        # Convert checklists
        html = self._convert_checklists(html)
        
        # Convert step lists
        html = self._convert_step_lists(html)
        
        # Convert section dividers
        html = self._convert_section_dividers(html)
        
        # Wrap in HTML document
        html = self._wrap_in_html(html, theme)
        
        return html
    
    def _convert_headers(self, text: str) -> str:
        """Convert Markdown headers to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML headers
        """
        # Headers with underscores
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Headers with dashes
        text = re.sub(r'^---\s*$', '<hr class="section-divider">', text, flags=re.MULTILINE)
        
        return text
    
    def _convert_emphasis(self, text: str) -> str:
        """Convert bold and italic Markdown to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML emphasis tags
        """
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        return text
    
    def _convert_lists(self, text: str) -> str:
        """Convert Markdown lists to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML lists
        """
        lines = text.split('\n')
        in_ul = False
        in_ol = False
        result = []
        
        for line in lines:
            # Unordered list
            ul_match = re.match(r'^[\-\*]\s+(.+)$', line)
            if ul_match:
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append('<ul>')
                    in_ul = True
                result.append(f'<li>{ul_match.group(1)}</li>')
                continue
            
            # Ordered list
            ol_match = re.match(r'^\d+\.\s+(.+)$', line)
            if ol_match:
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append('<ol>')
                    in_ol = True
                result.append(f'<li>{ol_match.group(1)}</li>')
                continue
            
            # Close lists if line doesn't match
            if in_ul and line.strip():
                result.append('</ul>')
                in_ul = False
            if in_ol and line.strip():
                result.append('</ol>')
                in_ol = False
            
            result.append(line)
        
        # Close any open lists
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')
        
        return '\n'.join(result)
    
    def _remove_code_blocks(self, text: str) -> str:
        """Remove code blocks as they're not user-friendly for clinical staff.
        
        Args:
            text: Markdown text
            
        Returns:
            Text without code blocks
        """
        # Remove fenced code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove indented code blocks
        text = re.sub(r'^( {4}|\t).+$', '', text, flags=re.MULTILINE)
        return text
    
    def _convert_inline_code(self, text: str) -> str:
        """Convert inline code to simple styled spans.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with styled inline code
        """
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text
    
    def _convert_horizontal_rules(self, text: str) -> str:
        """Convert horizontal rules to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML horizontal rules
        """
        text = re.sub(r'^-{3,}$', '<hr>', text, flags=re.MULTILINE)
        text = re.sub(r'^\*{3,}$', '<hr>', text, flags=re.MULTILINE)
        return text
    
    def _convert_links(self, text: str) -> str:
        """Convert Markdown links to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML links
        """
        # [text](url) format
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text
    
    def _convert_tables(self, text: str) -> str:
        """Convert Markdown tables to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML tables
        """
        lines = text.split('\n')
        in_table = False
        result = []
        table_rows = []
        
        for line in lines:
            if '|' in line:
                if not in_table:
                    in_table = True
                    table_rows = []
                
                # Skip separator rows (|---|---|)
                if re.match(r'^[\|\s\-:]+$', line):
                    continue
                
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')]
                cells = [c for c in cells if c]  # Remove empty cells
                table_rows.append(cells)
            else:
                if in_table and table_rows:
                    result.append(self._build_table(table_rows))
                    table_rows = []
                    in_table = False
                result.append(line)
        
        # Handle table at end of file
        if in_table and table_rows:
            result.append(self._build_table(table_rows))
        
        return '\n'.join(result)
    
    def _build_table(self, rows: List[List[str]]) -> str:
        """Build HTML table from parsed rows.
        
        Args:
            rows: List of table rows (each row is list of cells)
            
        Returns:
            HTML table string
        """
        if not rows:
            return ""
        
        html = ['<table>']
        
        # First row is header
        if rows:
            html.append('<tr>')
            for cell in rows[0]:
                html.append(f'<th>{cell}</th>')
            html.append('</tr>')
            
            # Remaining rows are data
            for row in rows[1:]:
                html.append('<tr>')
                for cell in row:
                    html.append(f'<td>{cell}</td>')
                html.append('</tr>')
        
        html.append('</table>')
        return '\n'.join(html)
    
    def _convert_blockquotes(self, text: str) -> str:
        """Convert Markdown blockquotes to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML blockquotes
        """
        lines = text.split('\n')
        in_blockquote = False
        result = []
        quote_lines = []
        
        for line in lines:
            if line.startswith('> '):
                if not in_blockquote:
                    in_blockquote = True
                    quote_lines = []
                quote_lines.append(line[2:])
            else:
                if in_blockquote:
                    result.append(f'<blockquote>{" ".join(quote_lines)}</blockquote>')
                    in_blockquote = False
                    quote_lines = []
                result.append(line)
        
        if in_blockquote and quote_lines:
            result.append(f'<blockquote>{" ".join(quote_lines)}</blockquote>')
        
        return '\n'.join(result)
    
    def _convert_callouts(self, text: str) -> str:
        """Convert special callout patterns to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML callout boxes
        """
        # Info callout: ℹ️ Info: text
        text = re.sub(
            r'ℹ️ Info:\s*(.+)$',
            r'<div class="callout callout-info">\1</div>',
            text,
            flags=re.MULTILINE
        )
        
        # Warning callout: ⚠️ Warning: text
        text = re.sub(
            r'⚠️ Warning:\s*(.+)$',
            r'<div class="callout callout-warning">\1</div>',
            text,
            flags=re.MULTILINE
        )
        
        # Danger callout: ❌ Danger: text
        text = re.sub(
            r'❌ Danger:\s*(.+)$',
            r'<div class="callout callout-danger">\1</div>',
            text,
            flags=re.MULTILINE
        )
        
        # Success callout: ✅ Success: text
        text = re.sub(
            r'✅ Success:\s*(.+)$',
            r'<div class="callout callout-success">\1</div>',
            text,
            flags=re.MULTILINE
        )
        
        return text
    
    def _convert_checklists(self, text: str) -> str:
        """Convert checklists (with ✅ or ❌) to styled HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with styled checklists
        """
        lines = text.split('\n')
        in_checklist = False
        in_crosslist = False
        result = []
        
        for line in lines:
            # Positive checklist
            if re.match(r'^[\-\*]\s+✅', line):
                if not in_checklist:
                    if in_crosslist:
                        result.append('</ul>')
                        in_crosslist = False
                    result.append('<ul class="checklist">')
                    in_checklist = True
                content = re.sub(r'^[\-\*]\s+✅\s*', '', line)
                result.append(f'<li>{content}</li>')
                continue
            
            # Negative checklist
            if re.match(r'^[\-\*]\s+❌', line):
                if not in_crosslist:
                    if in_checklist:
                        result.append('</ul>')
                        in_checklist = False
                    result.append('<ul class="checklist cross-list">')
                    in_crosslist = True
                content = re.sub(r'^[\-\*]\s+❌\s*', '', line)
                result.append(f'<li>{content}</li>')
                continue
            
            # Close lists
            if in_checklist and line.strip() and not re.match(r'^[\-\*]\s+✅', line):
                result.append('</ul>')
                in_checklist = False
            if in_crosslist and line.strip() and not re.match(r'^[\-\*]\s+❌', line):
                result.append('</ul>')
                in_crosslist = False
            
            result.append(line)
        
        if in_checklist:
            result.append('</ul>')
        if in_crosslist:
            result.append('</ul>')
        
        return '\n'.join(result)
    
    def _convert_step_lists(self, text: str) -> str:
        """Convert numbered step lists to styled HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with styled step lists
        """
        lines = text.split('\n')
        in_steps = False
        result = []
        step_lines = []
        
        for line in lines:
            # Step pattern: "Step 1:", "Step 2:", etc.
            step_match = re.match(r'^(Step \d+[:.]|###? Step \d+[:.])(.+)$', line, re.IGNORECASE)
            if step_match:
                if not in_steps:
                    in_steps = True
                    step_lines = []
                step_lines.append(step_match.group(2))
            else:
                if in_steps:
                    result.append('<ol class="step-list">')
                    for step in step_lines:
                        result.append(f'<li>{step}</li>')
                    result.append('</ol>')
                    in_steps = False
                    step_lines = []
                result.append(line)
        
        if in_steps and step_lines:
            result.append('<ol class="step-list">')
            for step in step_lines:
                result.append(f'<li>{step}</li>')
            result.append('</ol>')
        
        return '\n'.join(result)
    
    def _convert_section_dividers(self, text: str) -> str:
        """Convert section dividers to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            Text with HTML section dividers
        """
        # Pattern: "--- Text ---" or "*** Text ***"
        text = re.sub(
            r'^[-*]{3}\s+(.+?)\s+[-*]{3}$',
            r'<div class="section-divider">\1</div>',
            text,
            flags=re.MULTILINE
        )
        return text
    
    def _wrap_in_html(self, content: str, theme: str) -> str:
        """Wrap content in complete HTML document.
        
        Args:
            content: HTML content
            theme: Theme name
            
        Returns:
            Complete HTML document
        """
        html = f"""<!DOCTYPE html>
<html lang="en" data-theme="{theme}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Microscope Help</title>
    <style>
{self.css_content}
    </style>
</head>
<body>
{content}
</body>
</html>"""
        return html
    
    def convert_file(self, markdown_path: Path, output_path: Optional[Path] = None, theme: str = "light") -> str:
        """Convert a Markdown file to HTML.
        
        Args:
            markdown_path: Path to Markdown file
            output_path: Path to save HTML file (optional)
            theme: Theme name
            
        Returns:
            HTML content
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        html_content = self.convert(markdown_content, theme)
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Converted {markdown_path} to {output_path}")
        
        return html_content


def convert_all_markdown(docs_dir: Path, output_dir: Optional[Path] = None) -> Dict[str, str]:
    """Convert all Markdown files in a directory to HTML.
    
    Args:
        docs_dir: Directory containing Markdown files
        output_dir: Directory to save HTML files (optional)
        
    Returns:
        Dictionary of filename -> HTML content
    """
    converter = MarkdownToHTMLConverter()
    results = {}
    
    if output_dir is None:
        output_dir = docs_dir / "html"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for md_file in docs_dir.glob("*.md"):
        html_file = output_dir / (md_file.stem + ".html")
        html_content = converter.convert_file(md_file, html_file)
        results[md_file.stem] = html_content
    
    logger.info(f"Converted {len(results)} Markdown files to HTML")
    return results


if __name__ == "__main__":
    # Test conversion
    docs_dir = Path(__file__).parent.parent / "docs" / "user_facing"
    convert_all_markdown(docs_dir)

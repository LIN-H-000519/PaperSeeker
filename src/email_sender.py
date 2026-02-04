"""
Email Sender Module
Sends HTML formatted emails with paper recommendations
"""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

from .config import Config


class EmailSender:
    """Email sending handler"""

    def __init__(self, config: Config):
        """
        Initialize email sender

        Args:
            config: Configuration object
        """
        self.config = config
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.sender_email = config.sender_email
        self.sender_password = config.sender_password
        self.recipient_email = config.recipient_email

    def send(self, papers: List[Dict[str, Any]], date_str: str) -> bool:
        """
        Send paper recommendations email

        Args:
            papers: List of papers to send
            date_str: Date string for email subject

        Returns:
            True if successful
        """
        if not self.sender_email or not self.recipient_email:
            print("[Email] Email not configured, skipping send")
            return False

        subject = self.config.email_subject.format(date=date_str, count=len(papers))
        html_content = self._build_html_content(papers, date_str)

        return self._send_email(subject, html_content)

    def send_test(self) -> bool:
        """Send a test email"""
        subject = "PaperSeeker Test Email"
        html_content = """
        <html><body>
        <h2>PaperSeeker Test</h2>
        <p>If you receive this email, your PaperSeeker configuration is working correctly.</p>
        </body></html>
        """
        return self._send_email(subject, html_content)

    def send_empty_result(self, date_str: str) -> bool:
        """Send notification when no relevant papers found"""
        subject = self.config.email_subject.format(date=date_str, count=0)
        html_content = f"""
        <html><body>
        <h2>No Relevant Papers Found</h2>
        <p>Date: {date_str}</p>
        <p>No papers matched your research interests today.</p>
        <p>Consider adjusting your keywords in prompts.yaml for better results.</p>
        </body></html>
        """
        return self._send_email(subject, html_content)

    def _build_html_content(self, papers: List[Dict[str, Any]], date_str: str) -> str:
        """Build HTML email content"""
        greeting = self.config.email_greeting
        footer = self.config.email_footer.replace("\n", "<br>")

        paper_rows = ""
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Untitled")
            authors = paper.get("authors", "Unknown Authors")
            journal = paper.get("journal", "Unknown Journal")
            summary_zh = paper.get("summary_zh", "")
            summary_en = paper.get("summary_en", "")
            score = paper.get("relevance_score", 0)
            reason = paper.get("relevance_reason", "")
            openalex_url = paper.get("openalex_url", "")

            # Generate color based on score
            score_color = "#4CAF50" if score >= 4 else "#2196F3" if score >= 3 else "#FF9800"

            paper_rows += f"""
            <div class="paper-card">
                <div class="paper-header">
                    <span class="paper-number">{i}</span>
                    <span class="score-badge" style="background: {score_color}">{score}</span>
                    <h3 class="paper-title"><a href="{openalex_url}">{title}</a></h3>
                </div>
                <p class="paper-meta"><strong>{authors}</strong></p>
                <p class="paper-meta">{journal}</p>
                <div class="summary-section">
                    <p class="summary-zh">{summary_zh}</p>
                    <p class="summary-en">{summary_en}</p>
                </div>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; border-bottom: 2px solid #4CAF50; margin-bottom: 20px; }}
                .greeting {{ font-size: 16px; margin-bottom: 20px; }}
                .paper-card {{ background: #f9f9f9; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
                .paper-header {{ display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; }}
                .paper-number {{ background: #4CAF50; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }}
                .score-badge {{ color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; flex-shrink: 0; }}
                .paper-title {{ margin: 0; font-size: 16px; }}
                .paper-title a {{ color: #2196F3; text-decoration: none; }}
                .paper-title a:hover {{ text-decoration: underline; }}
                .paper-meta {{ margin: 5px 0; font-size: 13px; color: #666; }}
                .summary-section {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd; }}
                .summary-zh {{ font-size: 14px; color: #333; margin-bottom: 8px; }}
                .summary-en {{ font-size: 12px; color: #888; font-style: italic; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #888; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PaperSeeker</h1>
                <p>{date_str}</p>
            </div>
            <div class="greeting">{greeting}</div>
            <div class="papers">
                {paper_rows}
            </div>
            <div class="footer">
                {footer}
            </div>
        </body>
        </html>
        """

        return html

    def _send_email(self, subject: str, html_content: str) -> bool:
        """
        Send email via SMTP

        Args:
            subject: Email subject
            html_content: HTML content

        Returns:
            True if successful
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email

            # Add HTML part
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())

            print(f"[Email] Sent: {subject}")
            return True

        except Exception as e:
            print(f"[Email] Failed to send: {e}")
            return False

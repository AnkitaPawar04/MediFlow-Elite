"""Custom runserver command that auto-opens the browser."""
import webbrowser
import threading
from django.core.management.commands.runserver import Command as BaseRunserverCommand


class Command(BaseRunserverCommand):
    """Extended runserver command that opens browser to landing page."""
    
    def add_arguments(self, parser):
        """Add arguments to the command."""
        super().add_arguments(parser)
        parser.add_argument(
            '--no-browser',
            action='store_true',
            help='Do not open browser automatically',
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        # Open browser in a separate thread after a short delay
        if not options.get('no_browser', False):
            threading.Timer(2, self.open_browser).start()
        
        # Call the parent handle method
        super().handle(*args, **options)
    
    def open_browser(self):
        """Open the browser to the landing page."""
        try:
            url = 'http://127.0.0.1:8000/'
            webbrowser.open(url)
            print(f"\n✓ Opening browser to {url}\n")
        except Exception as e:
            print(f"Could not open browser: {e}")

import sys
import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, 
                              QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QTextEdit, QGroupBox, QSpinBox,
                              QMessageBox, QCheckBox, QTabWidget, QDialog,
                              QDialogButtonBox, QFormLayout)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor

# Configure logging
LOG_DIR = Path.home() / "TallySync" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"tally_sync_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PasswordManager:
    """Manage password protection for settings"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return PasswordManager.hash_password(password) == hashed
    
    @staticmethod
    def is_password_set(config: Dict) -> bool:
        """Check if password is set"""
        return 'settings_password' in config and config['settings_password']


class PasswordDialog(QDialog):
    """Password input dialog"""
    
    def __init__(self, parent=None, title="Enter Password", is_setup=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.is_setup = is_setup
        self.password = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        if self.is_setup:
            layout.addWidget(QLabel("Set up password protection for settings:"))
        else:
            layout.addWidget(QLabel("Enter password to access settings:"))
        
        form_layout = QFormLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)
        
        if self.is_setup:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow("Confirm:", self.confirm_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.setMinimumWidth(350)
    
    def validate_and_accept(self):
        """Validate password and accept"""
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty!")
            return
        
        if self.is_setup:
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return
            
            if len(password) < 4:
                QMessageBox.warning(self, "Error", "Password must be at least 4 characters!")
                return
        
        self.password = password
        self.accept()
    
    def get_password(self) -> Optional[str]:
        """Get entered password"""
        return self.password


class ChangePasswordDialog(QDialog):
    """Change password dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setModal(True)
        self.old_password = None
        self.new_password = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Current Password:", self.old_password_input)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("New Password:", self.new_password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm New:", self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.setMinimumWidth(350)
    
    def validate_and_accept(self):
        """Validate and accept"""
        old_pwd = self.old_password_input.text()
        new_pwd = self.new_password_input.text()
        confirm_pwd = self.confirm_password_input.text()
        
        if not old_pwd or not new_pwd:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return
        
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Error", "New passwords do not match!")
            return
        
        if len(new_pwd) < 4:
            QMessageBox.warning(self, "Error", "Password must be at least 4 characters!")
            return
        
        self.old_password = old_pwd
        self.new_password = new_pwd
        self.accept()


class TallyPrimeConnector:
    """Tally Prime/ERP 9 Connector"""
    
    def __init__(self, host: str = "localhost", port: int = 9000, company_name: Optional[str] = None):
        self.base_url = f"http://{host}:{port}"
        self.company_name = company_name
        self.headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        }
        self.tally_version = None
    
    def test_connection(self) -> bool:
        """Test Tally connection"""
        try:
            xml_request = """
            <ENVELOPE>
                <HEADER>
                    <VERSION>1</VERSION>
                    <TALLYREQUEST>Export</TALLYREQUEST>
                    <TYPE>Data</TYPE>
                    <ID>SysInfo</ID>
                </HEADER>
                <BODY>
                    <DESC>
                        <STATICVARIABLES>
                            <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        </STATICVARIABLES>
                    </DESC>
                </BODY>
            </ENVELOPE>
            """
            response = requests.post(
                self.base_url,
                data=xml_request.encode('utf-8'),
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_company_list(self) -> List[Dict]:
        """Get list of all companies"""
        xml_request = """
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>List of Companies</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        try:
            response = self._send_request(xml_request)
            return self._parse_collection(response, 'COMPANY')
        except:
            return []
    
    def get_ledgers(self) -> List[Dict]:
        """Fetch all ledgers"""
        xml_request = f"""
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>AllLedgers</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        {self._get_company_filter()}
                    </STATICVARIABLES>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        response = self._send_request(xml_request)
        return self._parse_collection(response, 'LEDGER')
    
    def get_stock_items(self) -> List[Dict]:
        """Fetch all stock items"""
        xml_request = f"""
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>AllStockItems</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        {self._get_company_filter()}
                    </STATICVARIABLES>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        response = self._send_request(xml_request)
        return self._parse_collection(response, 'STOCKITEM')
    
    def get_vouchers(self, from_date: str, to_date: str) -> List[Dict]:
        """Fetch vouchers for date range"""
        from_date = self._format_date(from_date)
        to_date = self._format_date(to_date)
        
        xml_request = f"""
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>VoucherCollection</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        <SVFROMDATE>{from_date}</SVFROMDATE>
                        <SVTODATE>{to_date}</SVTODATE>
                        {self._get_company_filter()}
                    </STATICVARIABLES>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        response = self._send_request(xml_request)
        return self._parse_collection(response, 'VOUCHER')
    
    def get_company_info(self) -> Dict:
        """Get current company information"""
        xml_request = f"""
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>CompanyInfo</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        {self._get_company_filter()}
                    </STATICVARIABLES>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        response = self._send_request(xml_request)
        return self._parse_xml_to_dict(response)
    
    def _get_company_filter(self) -> str:
        """Get company filter XML"""
        if self.company_name:
            return f"<SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>"
        return "<SVCURRENTCOMPANY>##SVCURRENTCOMPANY</SVCURRENTCOMPANY>"
    
    def _format_date(self, date_str: str) -> str:
        """Format date to Tally format (YYYYMMDD)"""
        date_str = date_str.replace('-', '')
        if len(date_str) == 8 and date_str.isdigit():
            return date_str
        return datetime.now().strftime('%Y%m%d')
    
    def _send_request(self, xml_request: str) -> str:
        """Send XML request to Tally"""
        try:
            response = requests.post(
                self.base_url,
                data=xml_request.encode('utf-8'),
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Tally request failed: {e}")
            raise
    
    def _parse_xml_to_dict(self, xml_string: str) -> Dict:
        """Parse XML to dictionary"""
        try:
            root = ET.fromstring(xml_string)
            return self._element_to_dict(root)
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            return {}
    
    def _element_to_dict(self, element) -> Dict:
        """Convert XML element to dict"""
        result = {}
        if element.text and element.text.strip():
            result['_text'] = element.text.strip()
        if element.attrib:
            result['_attributes'] = element.attrib
        for child in element:
            child_data = self._element_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        if len(result) == 1 and '_text' in result:
            return result['_text']
        return result
    
    def _parse_collection(self, xml_string: str, tag_name: str) -> List[Dict]:
        """Parse collection XML"""
        try:
            root = ET.fromstring(xml_string)
            items = []
            paths = [
                f'.//{tag_name}',
                f'.//BODY/DATA/COLLECTION/{tag_name}',
                f'.//BODY/IMPORTDATA/REQUESTDATA/{tag_name}'
            ]
            for path in paths:
                elements = root.findall(path)
                if elements:
                    for item in elements:
                        items.append(self._element_to_dict(item))
                    break
            return items
        except Exception as e:
            logger.error(f"Collection parsing failed: {e}")
            return []


class ServerSync:
    """Server synchronization handler"""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def test_connection(self) -> bool:
        """Test server connection"""
        try:
            response = requests.get(
                f"{self.server_url}/health",
                headers=self.headers,
                timeout=10
            )
            return response.status_code in [200, 404]
        except Exception as e:
            logger.error(f"Server connection test failed: {e}")
            return False
    
    def send_data(self, endpoint: str, data: Dict or List) -> Dict:
        """Send data to server"""
        try:
            url = f"{self.server_url}/{endpoint}"
            response = requests.post(
                url,
                json=data,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            return {'success': True, 'response': response.json() if response.text else {}}
        except Exception as e:
            logger.error(f"Server sync failed for {endpoint}: {e}")
            return {'success': False, 'error': str(e)}
    
    def batch_send(self, endpoint: str, data: List[Dict], batch_size: int = 100) -> Dict:
        """Send data in batches"""
        total = len(data)
        success_count = 0
        
        for i in range(0, total, batch_size):
            batch = data[i:i + batch_size]
            result = self.send_data(endpoint, batch)
            if result['success']:
                success_count += len(batch)
        
        return {
            'total': total,
            'success': success_count,
            'failed': total - success_count
        }


class SyncWorker(QThread):
    """Background sync worker thread"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.is_running = True
    
    def run(self):
        """Execute sync operation"""
        try:
            self.progress.emit("🔄 Starting sync...")
            
            tally = TallyPrimeConnector(
                self.config['tally_host'],
                self.config['tally_port'],
                self.config.get('company_name')
            )
            server = ServerSync(
                self.config['server_url'],
                self.config.get('api_key')
            )
            
            results = {
                'start_time': datetime.now().isoformat(),
                'success': True,
                'items_synced': {}
            }
            
            if self.config.get('sync_company', True):
                self.progress.emit("📊 Syncing company info...")
                company = tally.get_company_info()
                result = server.send_data('company', company)
                results['items_synced']['company'] = 1 if result['success'] else 0
            
            if self.config.get('sync_ledgers', True):
                self.progress.emit("📒 Syncing ledgers...")
                ledgers = tally.get_ledgers()
                result = server.batch_send('ledgers', ledgers, self.config.get('batch_size', 100))
                results['items_synced']['ledgers'] = result['success']
            
            if self.config.get('sync_stock', True):
                self.progress.emit("📦 Syncing stock items...")
                stock = tally.get_stock_items()
                result = server.batch_send('stock-items', stock, self.config.get('batch_size', 100))
                results['items_synced']['stock_items'] = result['success']
            
            if self.config.get('sync_vouchers', True):
                self.progress.emit("🧾 Syncing vouchers...")
                from_date = self.config.get('from_date', 
                    (datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
                to_date = self.config.get('to_date', 
                    datetime.now().strftime('%Y%m%d'))
                
                vouchers = tally.get_vouchers(from_date, to_date)
                result = server.batch_send('vouchers', vouchers, self.config.get('batch_size', 100))
                results['items_synced']['vouchers'] = result['success']
            
            results['end_time'] = datetime.now().isoformat()
            self.progress.emit("✅ Sync completed successfully!")
            self.finished.emit(results)
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.progress.emit(f"❌ Sync failed: {str(e)}")
            self.finished.emit({
                'success': False,
                'error': str(e),
                'end_time': datetime.now().isoformat()
            })


class ConfigManager:
    """Configuration manager"""
    
    CONFIG_DIR = Path.home() / "TallySync"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    @classmethod
    def load(cls) -> Dict:
        """Load configuration"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        return cls.get_default_config()
    
    @classmethod
    def save(cls, config: Dict):
        """Save configuration"""
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    @classmethod
    def get_default_config(cls) -> Dict:
        """Get default configuration"""
        return {
            'tally_host': 'localhost',
            'tally_port': 9000,
            'server_url': 'https://your-server.com/api',
            'api_key': '',
            'company_name': '',
            'sync_interval': 60,
            'batch_size': 100,
            'sync_company': True,
            'sync_ledgers': True,
            'sync_stock': True,
            'sync_vouchers': True,
            'auto_start': False,
            'start_minimized': False,
            'from_date': (datetime.now() - timedelta(days=1)).strftime('%Y%m%d'),
            'to_date': datetime.now().strftime('%Y%m%d'),
            'settings_password': ''
        }


class MainWindow(QWidget):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load()
        self.sync_worker = None
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.start_sync)
        self.settings_unlocked = False
        
        self.init_ui()
        self.load_config_to_ui()
        
        if not PasswordManager.is_password_set(self.config):
            self.setup_password()
        
        if self.config.get('auto_start', False):
            self.start_auto_sync()
    
    def setup_password(self):
        """Setup password for first time"""
        reply = QMessageBox.question(
            self,
            "Password Protection",
            "Would you like to set up password protection for settings?\n\n"
            "This will prevent unauthorized changes to your configuration.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            dialog = PasswordDialog(self, "Setup Password", is_setup=True)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = dialog.get_password()
                if password:
                    self.config['settings_password'] = PasswordManager.hash_password(password)
                    ConfigManager.save(self.config)
                    QMessageBox.information(
                        self,
                        "Success",
                        "Password protection enabled!\n\n"
                        "You will need this password to access settings."
                    )
                    self.lock_settings()
    
    def verify_password(self) -> bool:
        """Verify password before accessing settings"""
        if not PasswordManager.is_password_set(self.config):
            return True
        
        if self.settings_unlocked:
            return True
        
        dialog = PasswordDialog(self, "Unlock Settings")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.get_password()
            if password and PasswordManager.verify_password(password, self.config['settings_password']):
                self.settings_unlocked = True
                return True
            else:
                QMessageBox.warning(self, "Error", "Incorrect password!")
                return False
        return False
    
    def lock_settings(self):
        """Lock settings"""
        self.settings_unlocked = False
        self.disable_config_inputs()
    
    def disable_config_inputs(self):
        """Disable configuration inputs"""
        if hasattr(self, 'tally_host_input'):
            self.tally_host_input.setEnabled(self.settings_unlocked)
            self.tally_port_input.setEnabled(self.settings_unlocked)
            self.company_input.setEnabled(self.settings_unlocked)
            self.server_url_input.setEnabled(self.settings_unlocked)
            self.api_key_input.setEnabled(self.settings_unlocked)
            self.interval_input.setEnabled(self.settings_unlocked)
            self.batch_size_input.setEnabled(self.settings_unlocked)
            self.sync_company_cb.setEnabled(self.settings_unlocked)
            self.sync_ledgers_cb.setEnabled(self.settings_unlocked)
            self.sync_stock_cb.setEnabled(self.settings_unlocked)
            self.sync_vouchers_cb.setEnabled(self.settings_unlocked)
            self.auto_start_cb.setEnabled(self.settings_unlocked)
            self.start_minimized_cb.setEnabled(self.settings_unlocked)
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Tally Server Sync")
        self.setGeometry(100, 100, 800, 700)
        
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        tabs.addTab(self.create_config_tab(), "⚙️ Configuration")
        tabs.addTab(self.create_sync_tab(), "🔄 Sync")
        tabs.addTab(self.create_log_tab(), "📋 Logs")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        if PasswordManager.is_password_set(self.config):
            self.disable_config_inputs()
    
    def create_config_tab(self) -> QWidget:
        """Create configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        password_group = QGroupBox("Security")
        password_layout = QHBoxLayout()
        
        if PasswordManager.is_password_set(self.config):
            self.unlock_btn = QPushButton("🔓 Unlock Settings")
            self.unlock_btn.clicked.connect(self.unlock_settings)
            password_layout.addWidget(self.unlock_btn)
            
            self.lock_btn = QPushButton("🔒 Lock Settings")
            self.lock_btn.clicked.connect(self.lock_settings)
            password_layout.addWidget(self.lock_btn)
            
            change_pwd_btn = QPushButton("🔑 Change Password")
            change_pwd_btn.clicked.connect(self.change_password)
            password_layout.addWidget(change_pwd_btn)
            
            remove_pwd_btn = QPushButton("❌ Remove Password")
            remove_pwd_btn.clicked.connect(self.remove_password)
            password_layout.addWidget(remove_pwd_btn)
        else:
            setup_pwd_btn = QPushButton("🔒 Setup Password Protection")
            setup_pwd_btn.clicked.connect(self.setup_password)
            password_layout.addWidget(setup_pwd_btn)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        tally_group = QGroupBox("Tally Settings")
        tally_layout = QVBoxLayout()
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host:"))
        self.tally_host_input = QLineEdit()
        host_layout.addWidget(self.tally_host_input)
        tally_layout.addLayout(host_layout)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.tally_port_input = QSpinBox()
        self.tally_port_input.setRange(1, 65535)
        self.tally_port_input.setValue(9000)
        port_layout.addWidget(self.tally_port_input)
        tally_layout.addLayout(port_layout)
        
        company_layout = QHBoxLayout()
        company_layout.addWidget(QLabel("Company:"))
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Leave empty for current company")
        company_layout.addWidget(self.company_input)
        tally_layout.addLayout(company_layout)
        
        test_tally_btn = QPushButton("🔍 Test Tally Connection")
        test_tally_btn.clicked.connect(self.test_tally_connection)
        tally_layout.addWidget(test_tally_btn)
        
        tally_group.setLayout(tally_layout)
        layout.addWidget(tally_group)
        
        server_group = QGroupBox("Server Settings")
        server_layout = QVBoxLayout()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Server URL:"))
        self.server_url_input = QLineEdit()
        url_layout.addWidget(self.server_url_input)
        server_layout.addLayout(url_layout)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_layout.addWidget(self.api_key_input)
        server_layout.addLayout(key_layout)
        
        test_server_btn = QPushButton("🔍 Test Server Connection")
        test_server_btn.clicked.connect(self.test_server_connection)
        server_layout.addWidget(test_server_btn)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        sync_group = QGroupBox("Sync Settings")
        sync_layout = QVBoxLayout()
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Sync Interval (minutes):"))
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 1440)
        self.interval_input.setValue(60)
        interval_layout.addWidget(self.interval_input)
        sync_layout.addLayout(interval_layout)
        
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_input = QSpinBox()
        self.batch_size_input.setRange(10, 1000)
        self.batch_size_input.setValue(100)
        batch_layout.addWidget(self.batch_size_input)
        sync_layout.addLayout(batch_layout)
        
        self.sync_company_cb = QCheckBox("Sync Company Info")
        self.sync_ledgers_cb = QCheckBox("Sync Ledgers")
        self.sync_stock_cb = QCheckBox("Sync Stock Items")
        self.sync_vouchers_cb = QCheckBox("Sync Vouchers")
        self.auto_start_cb = QCheckBox("Auto-start sync on launch")
        self.start_minimized_cb = QCheckBox("Start minimized to tray")
        
        sync_layout.addWidget(self.sync_company_cb)
        sync_layout.addWidget(self.sync_ledgers_cb)
        sync_layout.addWidget(self.sync_stock_cb)
        sync_layout.addWidget(self.sync_vouchers_cb)
        sync_layout.addWidget(self.auto_start_cb)
        sync_layout.addWidget(self.start_minimized_cb)
        
        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)
        
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def unlock_settings(self):
        """Unlock settings"""
        if self.verify_password():
            self.disable_config_inputs()
            QMessageBox.information(self, "Success", "Settings unlocked!")
    
    def change_password(self):
        """Change password"""
        dialog = ChangePasswordDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            old_pwd = dialog.old_password
            new_pwd = dialog.new_password
            
            if PasswordManager.verify_password(old_pwd, self.config['settings_password']):
                self.config['settings_password'] = PasswordManager.hash_password(new_pwd)
                ConfigManager.save(self.config)
                QMessageBox.information(self, "Success", "Password changed successfully!")
            else:
                QMessageBox.warning(self, "Error", "Current password is incorrect!")
    
    def remove_password(self):
        """Remove password protection"""
        dialog = PasswordDialog(self, "Confirm Password Removal")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.get_password()
            if PasswordManager.verify_password(password, self.config['settings_password']):
                reply = QMessageBox.question(
                    self,
                    "Confirm",
                    "Are you sure you want to remove password protection?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.config['settings_password'] = ''
                    ConfigManager.save(self.config)
                    self.settings_unlocked = True
                    QMessageBox.information(self, "Success", "Password protection removed!")
            else:
                QMessageBox.warning(self, "Error", "Incorrect password!")
    
    def create_sync_tab(self) -> QWidget:
        """Create sync tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        
        self.sync_now_btn = QPushButton("▶️ Sync Now")
        self.sync_now_btn.clicked.connect(self.start_sync)
        btn_layout.addWidget(self.sync_now_btn)
        
        self.auto_sync_btn = QPushButton("🔄 Start Auto Sync")
        self.auto_sync_btn.clicked.connect(self.toggle_auto_sync)
        btn_layout.addWidget(self.auto_sync_btn)
        
        layout.addLayout(btn_layout)
        
        status_group = QGroupBox("Sync Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(self.status_label)
        
        self.last_sync_label = QLabel("Last Sync: Never")
        status_layout.addWidget(self.last_sync_label)
        
        self.next_sync_label = QLabel("Next Sync: Not scheduled")
        status_layout.addWidget(self.next_sync_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        log_group = QGroupBox("Sync Progress")
        log_layout = QVBoxLayout()
        
        self.progress_log = QTextEdit()
        self.progress_log.setReadOnly(True)
        log_layout.addWidget(self.progress_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_log_tab(self) -> QWidget:
        """Create log tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Logs")
        refresh_btn.clicked.connect(self.load_logs)
        btn_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear Display")
        clear_btn.clicked.connect(lambda: self.log_display.clear())
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        widget.setLayout(layout)
        self.load_logs()
        return widget
    
    def load_config_to_ui(self):
        """Load configuration to UI"""
        self.tally_host_input.setText(self.config.get('tally_host', 'localhost'))
        self.tally_port_input.setValue(self.config.get('tally_port', 9000))
        self.company_input.setText(self.config.get('company_name', ''))
        self.server_url_input.setText(self.config.get('server_url', ''))
        self.api_key_input.setText(self.config.get('api_key', ''))
        self.interval_input.setValue(self.config.get('sync_interval', 60))
        self.batch_size_input.setValue(self.config.get('batch_size', 100))
        
        self.sync_company_cb.setChecked(self.config.get('sync_company', True))
        self.sync_ledgers_cb.setChecked(self.config.get('sync_ledgers', True))
        self.sync_stock_cb.setChecked(self.config.get('sync_stock', True))
        self.sync_vouchers_cb.setChecked(self.config.get('sync_vouchers', True))
        self.auto_start_cb.setChecked(self.config.get('auto_start', False))
        self.start_minimized_cb.setChecked(self.config.get('start_minimized', False))
    
    def save_config(self):
        """Save configuration"""
        if not self.verify_password():
            return
        
        self.config['tally_host'] = self.tally_host_input.text()
        self.config['tally_port'] = self.tally_port_input.value()
        self.config['company_name'] = self.company_input.text()
        self.config['server_url'] = self.server_url_input.text()
        self.config['api_key'] = self.api_key_input.text()
        self.config['sync_interval'] = self.interval_input.value()
        self.config['batch_size'] = self.batch_size_input.value()
        
        self.config['sync_company'] = self.sync_company_cb.isChecked()
        self.config['sync_ledgers'] = self.sync_ledgers_cb.isChecked()
        self.config['sync_stock'] = self.sync_stock_cb.isChecked()
        self.config['sync_vouchers'] = self.sync_vouchers_cb.isChecked()
        self.config['auto_start'] = self.auto_start_cb.isChecked()
        self.config['start_minimized'] = self.start_minimized_cb.isChecked()
        
        ConfigManager.save(self.config)
        QMessageBox.information(self, "Success", "Configuration saved successfully!")
    
    def test_tally_connection(self):
        """Test Tally connection"""
        tally = TallyPrimeConnector(
            self.tally_host_input.text(),
            self.tally_port_input.value()
        )
        
        if tally.test_connection():
            QMessageBox.information(self, "Success", "✅ Connected to Tally successfully!")
        else:
            QMessageBox.warning(self, "Error", "❌ Failed to connect to Tally.\n\nPlease check:\n- Tally is running\n- XML API is enabled (F12 → Advanced Config)\n- Host and port are correct")
    
    def test_server_connection(self):
        """Test server connection"""
        server = ServerSync(
            self.server_url_input.text(),
            self.api_key_input.text() or None
        )
        
        if server.test_connection():
            QMessageBox.information(self, "Success", "✅ Connected to server successfully!")
        else:
            QMessageBox.warning(self, "Error", "❌ Failed to connect to server.\n\nPlease check:\n- Server URL is correct\n- API key is valid\n- Server is accessible")
    
    def start_sync(self):
        """Start sync operation"""
        if self.sync_worker and self.sync_worker.isRunning():
            QMessageBox.warning(self, "Warning", "Sync is already in progress!")
            return
        
        self.progress_log.clear()
        self.status_label.setText("Status: Syncing...")
        self.sync_now_btn.setEnabled(False)
        
        self.sync_worker = SyncWorker(self.config)
        self.sync_worker.progress.connect(self.update_progress)
        self.sync_worker.finished.connect(self.sync_finished)
        self.sync_worker.start()
    
    def update_progress(self, message: str):
        """Update progress log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.progress_log.append(f"[{timestamp}] {message}")
    
    def sync_finished(self, results: Dict):
        """Handle sync completion"""
        self.sync_now_btn.setEnabled(True)
        
        if results.get('success'):
            self.status_label.setText("Status: Idle")
            self.last_sync_label.setText(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            items = results.get('items_synced', {})
            summary = "\n".join([f"{k}: {v}" for k, v in items.items()])
            self.update_progress(f"\n📊 Sync Summary:\n{summary}")
        else:
            self.status_label.setText("Status: Failed")
            error = results.get('error', 'Unknown error')
            self.update_progress(f"\n❌ Error: {error}")
    
    def toggle_auto_sync(self):
        """Toggle auto sync"""
        if self.sync_timer.isActive():
            self.stop_auto_sync()
        else:
            self.start_auto_sync()
    
    def start_auto_sync(self):
        """Start auto sync"""
        interval_ms = self.config.get('sync_interval', 60) * 60 * 1000
        self.sync_timer.start(interval_ms)
        self.auto_sync_btn.setText("⏸️ Stop Auto Sync")
        self.update_next_sync_time()
        self.start_sync()
    
    def stop_auto_sync(self):
        """Stop auto sync"""
        self.sync_timer.stop()
        self.auto_sync_btn.setText("🔄 Start Auto Sync")
        self.next_sync_label.setText("Next Sync: Not scheduled")
    
    def update_next_sync_time(self):
        """Update next sync time display"""
        if self.sync_timer.isActive():
            interval_min = self.config.get('sync_interval', 60)
            next_time = datetime.now() + timedelta(minutes=interval_min)
            self.next_sync_label.setText(f"Next Sync: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def load_logs(self):
        """Load log file"""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, 'r') as f:
                    self.log_display.setPlainText(f.read())
        except Exception as e:
            self.log_display.setPlainText(f"Failed to load logs: {e}")


class SystemTrayApp(QApplication):
    """System tray application"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        self.main_window = MainWindow()
        
        self.tray_icon = QSystemTrayIcon(self.create_icon(), self)
        self.tray_icon.setToolTip("Tally Server Sync")
        
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        sync_action = QAction("Sync Now", self)
        sync_action.triggered.connect(self.main_window.start_sync)
        tray_menu.addAction(sync_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        if self.main_window.config.get('start_minimized', False):
            self.main_window.hide()
        else:
            self.main_window.show()
    
    def create_icon(self) -> QIcon:
        """Create tray icon"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setBrush(QColor(76, 175, 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()
        
        return QIcon(pixmap)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show main window"""
        self.main_window.show()
        self.main_window.activateWindow()
    
    def quit_app(self):
        """Quit application"""
        self.main_window.stop_auto_sync()
        self.quit()


def main():
    """Main entry point"""
    app = SystemTrayApp(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

from log.logger import setup_logger

logger = setup_logger("keywords_logs")


PREDEFINED_KEYWORDS = {
    "Water": [
        "Automation", "SCADA", "RTU","Remote Terminal Unit", "Lift Irrigation", "Irrigation Control",
        "Crop Monitoring", "Tunnel Automation", "Barrage Automation",
        "Water Distribution", "Agricultural Surveillance", "Remote Sensing",
        "Crop Health Assessment", "Satellite Imagery", "Yield Prediction",
        "Farm Management Systems", "Vegetation Index", "Plant Disease Detection",
        "Field Data Collection", "Geospatial Analysis", "Crop Management Software",
        "Smart Farming", "River Integration", "Radar Level Transmitter",
        "Turbidity Analyzer", "HMI","Human Machine Interface", "Chlorine Analyser", "Flowmeter",
        "Electromagnetic Flow Meter", "Ultrasonic Level Transmitter",
        "Level Transmitter", "VFD","Variable Frequency Drive", "Pressure Transmitter"
    ],
    "Oil & Gas": [
        "CTSU","Computerized Test Station Unit","DATA Logger", "Cathodic Protection", "Remote Monitoring", "Automation", "Digital TR","Digital Transformer Rectifier", "Transformer Rectifier",
        "SRP Automation","Sucker Rod Pump Automation","Cathodic Protection"
    ],
    "Lighting": [
        "CCMS","Centralized Control and Monitoring System", "Smart Light Controller", "RTU","Remote Terminal Unit", "RMU","Ring Main Unit"
    ]
}

logger.debug("Keywords loaded successfully.")
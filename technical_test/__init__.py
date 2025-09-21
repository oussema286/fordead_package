"""
Technical Test - Early Bark Beetle Detection with Sentinel Data

Pipeline modulaire pour la détection précoce des perturbations forestières
avec focus sur les épidémies de scolytes.
"""

__version__ = "1.0.0"
__author__ = "Technical Test Implementation"
__description__ = "Early Bark Beetle Detection with Sentinel Data"

from .data_ingestion_gee import Sentinel2IngestionGEE
from .change_detection import RupturesDetector
from .wind_analysis import WindBeetleClassifier
from .evaluation import DisturbanceEvaluator
from .fordead_wrapper_real import FordeadWrapperReal

__all__ = [
    "Sentinel2IngestionGEE", 
    "RupturesDetector",
    "WindBeetleClassifier",
    "DisturbanceEvaluator",
    "FordeadWrapperReal"
]

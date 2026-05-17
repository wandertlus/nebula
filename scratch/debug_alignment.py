import sys
import os
sys.path.append('/Users/dokodo/Desktop/nebula')

from nebula_processor import ProjectNebulaProcessor
from config import CONFIG

proc = ProjectNebulaProcessor(CONFIG)
text = "code for the project"
alignments = proc.calculate_alignment(text)
print(f"Text: {text}")
print(f"Alignments: {alignments}")

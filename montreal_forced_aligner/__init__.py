"""Montreal Forced Aligner is a package for aligning speech corpora through the use of acoustic models and
            dictionaries using Kaldi functionality."""
import os
os.environ["OMP_NUM_THREADS"] = "1" # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "1" # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import montreal_forced_aligner.acoustic_modeling as acoustic_modeling
import montreal_forced_aligner.alignment as alignment
import montreal_forced_aligner.command_line as command_line
import montreal_forced_aligner.corpus as corpus
import montreal_forced_aligner.dictionary as dictionary
import montreal_forced_aligner.exceptions as exceptions
import montreal_forced_aligner.g2p as g2p
import montreal_forced_aligner.helper as helper
import montreal_forced_aligner.ivector as ivector
import montreal_forced_aligner.language_modeling as language_modeling
import montreal_forced_aligner.models as models
import montreal_forced_aligner.textgrid as textgrid
import montreal_forced_aligner.transcription as transcription
import montreal_forced_aligner.utils as utils

__all__ = [
    "abc",
    "data",
    "acoustic_modeling",
    "alignment",
    "command_line",
    "config",
    "corpus",
    "dictionary",
    "exceptions",
    "g2p",
    "ivector",
    "language_modeling",
    "helper",
    "models",
    "transcription",
    "textgrid",
    "utils",
]

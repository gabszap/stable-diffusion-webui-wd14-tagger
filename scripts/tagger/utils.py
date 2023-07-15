import os

from typing import List, Dict
from pathlib import Path

from modules import shared, scripts
from preload import default_ddp_path, default_onnx_path
from scripts.tagger.preset import Preset
from scripts.tagger.interrogator import Interrogator, DeepDanbooruInterrogator
from scripts.tagger.interrogator import WaifuDiffusionInterrogator

preset = Preset(Path(scripts.basedir(), 'presets'))

interrogators: Dict[str, Interrogator] = {}


def refresh_interrogators() -> List[str]:
    """Refreshes the interrogators list"""
    global interrogators
    interrogators = {
        'wd14-convnextv2-v2': WaifuDiffusionInterrogator(
            'wd14-convnextv2-v2',
            repo_id='SmilingWolf/wd-v1-4-convnextv2-tagger-v2',
            revision='v2.0'
        ),
        'wd14-vit-v2': WaifuDiffusionInterrogator(
            'wd14-vit-v2',
            repo_id='SmilingWolf/wd-v1-4-vit-tagger-v2',
            revision='v2.0'
        ),
        'wd14-convnext-v2': WaifuDiffusionInterrogator(
            'wd14-convnext-v2',
            repo_id='SmilingWolf/wd-v1-4-convnext-tagger-v2',
            revision='v2.0'
        ),
        'wd14-swinv2-v2': WaifuDiffusionInterrogator(
            'wd14-swinv2-v2',
            repo_id='SmilingWolf/wd-v1-4-swinv2-tagger-v2',
            revision='v2.0'
        ),
        'wd14-convnextv2-v2-git': WaifuDiffusionInterrogator(
            'wd14-convnextv2-v2',
            repo_id='SmilingWolf/wd-v1-4-convnextv2-tagger-v2',
        ),
        'wd14-vit-v2-git': WaifuDiffusionInterrogator(
            'wd14-vit-v2-git',
            repo_id='SmilingWolf/wd-v1-4-vit-tagger-v2'
        ),
        'wd14-convnext-v2-git': WaifuDiffusionInterrogator(
            'wd14-convnext-v2-git',
            repo_id='SmilingWolf/wd-v1-4-convnext-tagger-v2'
        ),
        'wd14-swinv2-v2-git': WaifuDiffusionInterrogator(
            'wd14-swinv2-v2-git',
            repo_id='SmilingWolf/wd-v1-4-swinv2-tagger-v2'
        ),
        'wd14-vit': WaifuDiffusionInterrogator(
            'wd14-vit',
            repo_id='SmilingWolf/wd-v1-4-vit-tagger'
        ),
        'wd14-convnext': WaifuDiffusionInterrogator(
            'wd14-convnext',
            repo_id='SmilingWolf/wd-v1-4-convnext-tagger'
        ),
        'wd-v1-4-moat-tagger-v2': WaifuDiffusionInterrogator(
            'wd-v1-4-moat-tagger-v2',
            repo_id='SmilingWolf/wd-v1-4-moat-tagger-v2'
        ),
        #'Z3D-E621-Convnext': WaifuDiffusionInterrogator('Z3D-E621-Convnext'),
    }

    # load deepdanbooru project
    ddp_path = getattr(shared.cmd_opts, 'deepdanbooru_projects_path',
                       default_ddp_path)
    onnx_path = getattr(shared.cmd_opts, 'onnxtagger_path', default_onnx_path)
    os.makedirs(ddp_path, exist_ok=True)
    os.makedirs(onnx_path, exist_ok=True)

    for path in os.scandir(ddp_path):
        print(f"Scanning {path} as deepdanbooru project")
        if not path.is_dir():
            print(f"Warning: {path} is not a directory, skipped")
            continue

        if not Path(path, 'project.json').is_file():
            print(f"Warning: {path} has no project.json, skipped")
            continue

        interrogators[path.name] = DeepDanbooruInterrogator(path.name, path)
    # scan for onnx models as well
    for path in os.scandir(onnx_path):
        print(f"Scanning {path} as onnx model")
        if not path.is_dir():
            print(f"Warning: {path} is not a directory, skipped")
            continue

        onnx_files = [x for x in os.scandir(path) if x.name.endswith('.onnx')]
        if len(onnx_files) != 1:
            print(f"Warning: {path} requires exactly one .onnx model, skipped")
            continue
        model_path = Path(path, onnx_files[0].name)

        csv = [x for x in os.scandir(path) if x.name.endswith('.csv')]
        if len(csv) == 0:
            print(f"Warning: {path} has no selected tags .csv file, skipped")
            continue

        def tag_select_csvs_up_front(k):
            sum(-1 if t in k.name.lower() else 1 for t in ["tag", "select"])

        csv.sort(key=tag_select_csvs_up_front)
        tags_path = Path(path, csv[0])

        if path.name not in interrogators:
            if path.name == 'wd-v1-4-convnextv2-tagger-v2':
                interrogators[path.name] = WaifuDiffusionInterrogator(
                    path.name,
                    repo_id='SmilingWolf/SW-CV-ModelZoo'
                )
            elif path.name == 'Z3D-E621-Convnext':
                interrogators[path.name] = WaifuDiffusionInterrogator(
                    'Z3D-E621-Convnext')
            else:
                raise NotImplementedError(f"Add {path.name} resolution similar"
                                          "to above here")

        interrogators[path.name].model_path = model_path
        interrogators[path.name].tags_path = tags_path

    return sorted(interrogators.keys())


def split_str(string: str, separator=',') -> List[str]:
    return [x.strip() for x in string.split(separator) if x]

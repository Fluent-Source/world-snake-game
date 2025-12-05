from typing import Optional

import yaml
from pydantic import BaseModel, ValidationError


class WindowSettings(BaseModel):
  width: int
  height: int
  title: str


class GridSettings(BaseModel):
  draw: bool
  width: int
  height: int


class ColorsSettings(BaseModel):
  background: str
  grid: str
  select: str
  snake: str
  wall: str
  text: str


class PathSettings(BaseModel):
  dir: str  # noqa: A003 – keep key name identical to YAML for convenience
  level: str


class GameSettings(BaseModel):
  speed: int
  width: int


class Config(BaseModel):
  window: WindowSettings
  grid: GridSettings
  colors: ColorsSettings
  wall: float
  path: PathSettings
  game: GameSettings


def load_config(path: str = "config.yaml") -> Optional[Config]:
  """Load and validate the project configuration.

  Parameters
  ----------
  path: str, optional
      Location of the YAML file. Defaults to ``config.yaml`` relative to the
      working directory.

  Returns
  -------
  Optional[Config]
      A fully-validated :class:`Config` object, or *None* if the file is not
      found, cannot be parsed, or fails validation. Any problems are printed
      to *stdout* so that the caller can decide how to proceed.
  """
  try:
    with open(path, "r", encoding="utf-8") as file:
      raw = yaml.safe_load(file)
    return Config(**raw)

  except FileNotFoundError:
    print(f"Error: Config file '{path}' not found.")

  except yaml.YAMLError as exc:
    print(f"Error parsing YAML file: {exc}")

  except ValidationError as exc:
    # Pretty-print validation errors using Pydantic's JSON representation
    print("Error validating configuration:")
    print(exc.json(indent=2))

  # Something went wrong – signal failure to caller
  return None

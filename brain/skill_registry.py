import importlib
import pkgutil
import skills
from skills.base_skill import BaseSkill


class SkillRegistry:

    def __init__(self):
        self.skills = []
        self._load_skills()

    def _load_skills(self):
        for _, module_name, _ in pkgutil.iter_modules(skills.__path__):
            if module_name == "base_skill":
                continue

            try:
                module = importlib.import_module(f"skills.{module_name}")

                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, BaseSkill) and obj is not BaseSkill:
                        self.skills.append(obj())
            except Exception as e:
                print(f"Failed to load skill {module_name}: {e}")

    def get_all_skills(self):
        return self.skills

    def get_skill(self, name: str):
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None

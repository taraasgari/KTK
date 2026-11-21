from dataclasses import dataclass, field


@dataclass
class StoreDesign:
    colors: dict = field(default_factory=dict)
    typography: dict = field(default_factory=dict)
    layout: dict = field(default_factory=dict)
    components: dict = field(default_factory=dict)
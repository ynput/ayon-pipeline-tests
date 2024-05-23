
from ayon_server.addons import BaseServerAddon

class PipelineTestsAddon(BaseServerAddon):

    def __init__(
            self,
            definition: "ServerAddonDefinition",
            addon_dir: str,
            **kwargs
    ):
        super().__init__(definition, addon_dir, **kwargs)

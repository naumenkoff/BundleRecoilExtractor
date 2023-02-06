import UnityPy


class BundleDumper:

    def __init__(self, bundle_dir):
        self.env = UnityPy.load(bundle_dir)
        print("Loaded 'content.bundle'.")

    def dump_assets(self):

        dump = {
            'weapons': {},
            'attachments': {}
        }

        for obj in self.env.objects:
            
            # We only need objects of the GameObject type
            if obj.type.name != "GameObject": continue
            
            # Here we get a file that contains scripts inside itself - this is prefab
            # For example => assets/prefabs/weapon mods/holosight/holosight.entity.prefab
            data = obj.read()
            
            if data.container is None: continue

            # We only need weapons and attachments, we don't need anything else like pools prefabs.
            if not('assets/prefabs/weapons' in data.container or 'assets/prefabs/weapon mods' in data.container): continue

            # We only need 'entity', 'viewmodel', 'attachment'. 
            # We don't need other prefabs like '.worldmodel'
            if not (data.name.split(".")[-1] in ['entity', 'viewmodel', 'attachment']): continue
            
            # We get the pure name of the prefab - either a weapon or an attachment.
            prefab_name = data.name.partition(".")[0]

            # Here we get the nested scripts of the current prefab # PPtr
            for component in data.m_Components:

                # We only need scripts of the MonoBehaviour type
                if not (str(component.type.name) == "MonoBehaviour"): continue

                # Here we get the contents of the iterated script
                cdata = component.get_obj().read()

                # Here we get the type of iterated script
                cscript = cdata.m_Script.get_obj().read().name             

                # Weapon Handler
                if cscript in ['IronSights', 'BaseProjectile']:
                    
                    # If there is no section with the name of the iterated weapon in dump, create this section.
                    if not (prefab_name in dump['weapons']): dump['weapons'][prefab_name] = {}

                    # RecoilProperties Section
                    if cscript == "BaseProjectile":

                        recoil = cdata.type_tree.recoil.get_obj().read()

                        if recoil.type_tree.newRecoilOverride.type.name == "MonoBehaviour":
                            recoil = recoil.type_tree.newRecoilOverride.get_obj().read()

                        type_tree = recoil.read_typetree()
                        
                        dump['weapons'][prefab_name]['RecoilProperties'] = type_tree

                    # IronSights Section
                    dump['weapons'][prefab_name][cscript] = cdata.read_typetree()

                
                if cscript in ['IronSightOverride', 'ProjectileWeaponMod']:
                    
                    # If there is no section with the name of the iterated attachment in dump, create this section.
                    if not (prefab_name in dump['attachments']): dump['attachments'][prefab_name] = {}

                    # Attachment Handler => Here we get a real IronSightOverride
                    if cscript == 'IronSightOverride':
                        if '.vm.attachment.prefab' in data.container:
                            dump['attachments'][prefab_name][cscript] = cdata.read_typetree()

                    # Attachment Handler => Here we get a real ProjectileWeaponMod
                    if cscript == 'ProjectileWeaponMod':
                        if '.entity.prefab' in data.container:
                            dump['attachments'][prefab_name][cscript] = cdata.read_typetree()

        not_weapons = [key for key in list(dump['weapons'].keys()) if len(list(dump['weapons'][key].keys())) < 3]
        for i in not_weapons:
            del dump['weapons'][i]
     
        not_attachments = [
            key for key in list(dump['attachments'].keys())
            if not ('IronSightOverride' in list(dump['attachments'][key].keys()) or 'ProjectileWeaponMod' in list(dump['attachments'][key].keys()))]
        for i in not_attachments:
            del dump['attachments'][i]

        return dump

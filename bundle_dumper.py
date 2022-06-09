import UnityPy
import time

class BundleDumper:
    
    def __init__(self, bundle_dir):

        # Will store MonoScript objects that we need.
        self.mono_scripts = {
            "BaseProjectile"        : None,
            "IronSights"            : None,
            "ProjectileWeaponMod"   : None,
            "IronSightOverride"     : None
        }

        # Will store found attachments
        self.attachments = {}

        # Load the content.bundle file
        self.env = UnityPy.load(bundle_dir)

        # Loop through objects in the environment
        for obj in self.env.objects:

            # Check if all MonoScripts have been found. If not, parse each MonoScript object.
            if type(None) in [type(i) for i in list(self.mono_scripts.values())] and str(obj.type) == "ClassIDType.MonoScript":

                # Read the object data.
                data = obj.read()

                # Check if data name is within our dict of wanted types
                if not data.name in self.mono_scripts: continue

                # Store the matched data
                self.mono_scripts[data.name] = data
    
    def monoscripts_found(self) -> bool:

        # Check if all monoscripts have been found successfully
        return not (type(None) in [type(i) for i in list(self.mono_scripts.values())])
    
    def dump_assets(self):

        # Will store the final dump object
        dump = {
            'weapons':{},
            'attachments':{}
        }

        # Loop through objects again.
        for obj in self.env.objects:

            # Check object type is GameObject
            if str(obj.type) == "ClassIDType.GameObject":

                # Read the object data
                data = obj.read()

                # Skip NoneType containers
                if data.container == None: continue

                # Skip unwanted objects
                if not ("assets/prefabs/weapons" in data.container or "assets/prefabs/weapon mods" in data.container): continue

                # Skip unwanted prefabs
                if not data.name.split(".")[-1] in ['entity', 'viewmodel', 'attachment']: continue

                # Get the weapon raw name
                weapon_name = data.name.replace(".viewmodel", "").replace(".entity", "").replace(".vm.attachment", "")

                # Create the weapon entry
                if not weapon_name in dump['weapons']: dump['weapons'][weapon_name] = {}

                # Create the attachment entry
                if not weapon_name in dump['attachments']: dump['attachments'][weapon_name] = {}

                # Loop through components
                for component in data.m_Components:
                    
                    # Skip anything that isn't MonoBehaviour
                    if not str(component.type) == "ClassIDType.MonoBehaviour": continue

                    # Get the object data
                    cdata = component.get_obj().read()

                    # Get current MonoBehaviour script name
                    cscript = cdata.m_Script.get_obj().read().name
                    
                    # Check if the script is for a weapon.
                    if cscript in ['IronSights', 'BaseProjectile']:

                        # Check for the BaseProjectile script
                        if cscript == "BaseProjectile":

                            # Get the RecoilProperties for the BaseProjectile entry
                            recoil = cdata.type_tree.recoil.get_obj().read()

                            # We need to check for an override.
                            if not ("Not Found" in str(recoil.type_tree.newRecoilOverride)):

                                # Update the recoil with the override.
                                recoil = recoil.type_tree.newRecoilOverride.get_obj().read()

                            # Store the data RecoilProperties for this BaseProjectile entry
                            dump['weapons'][weapon_name]['RecoilProperties'] = recoil.read_typetree()

                        # Store the data
                        dump['weapons'][weapon_name][cscript] = cdata.read_typetree()
                    
                    # Check if the script is for an attachment
                    if cscript in ['ProjectileWeaponMod', 'IronSightOverride']:

                        # Store the data
                        dump['attachments'][weapon_name][cscript] = cdata.read_typetree()
        
        # Determine unwanted weapons in the list.
        unwanted = [key for key in list(dump['weapons'].keys()) if len(list(dump['weapons'][key].keys())) < 3]

        # Loop through and delete all unwanted weapons
        for j in unwanted: del dump['weapons'][j]

        # Determine unwanted weapons in the list. MESSY CODE WARNING :D
        unwanted = [
            key for key in list(dump['attachments'].keys()) 
            if not ('IronSightOverride' in list(dump['attachments'][key].keys()) 
            or 'ProjectileWeaponMod'in list(dump['attachments'][key].keys()))
        ]

        # Loop through and delete all unwanted weapons
        for j in unwanted: del dump['attachments'][j]

        # Return dumped weapons
        return dump
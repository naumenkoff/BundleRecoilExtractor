class DumpParser:

    def __init__(self, dump):
        self.dump = dump

    def parse_attachments(self):
        parsed_attachments = []
        
        for name, content in self.dump['attachments'].items():
            parsed_attachment = {'name': name, 'modifiers': {}}
            
            if ('IronSightOverride' in content):
                parsed_attachment['fov-bias'] = content['IronSightOverride']['fovBias']
                parsed_attachment['fov-offset'] = content['IronSightOverride']['fieldOfViewOffset']
                parsed_attachment['zoom-factor'] = content['IronSightOverride']['zoomFactor']
                parsed_attachment['type'] = 'Scope'
            
            if ('ProjectileWeaponMod' in content):
                if ('type' not in parsed_attachment):
                    if content['ProjectileWeaponMod']['isSilencer'] or content['ProjectileWeaponMod']['isMuzzleBrake'] or content['ProjectileWeaponMod']['isMuzzleBoost']:
                        parsed_attachment['type'] = 'Barrel'
                parsed_attachment['modifiers'] = {
                    'recoil': content['ProjectileWeaponMod']['recoil'],
                    'repeat-delay': content['ProjectileWeaponMod']['repeatDelay']
                    }

            parsed_attachments.append(parsed_attachment)

        return parsed_attachments

    def parse_weapons(self):

        parsed_weapons = []

        for k, v in self.dump['weapons'].items():
            parsed_weapon = {'m_Name': k}
            if ("RecoilProperties" in v):
                parsed_weapon['recoilPitchMin'] = v['RecoilProperties']['recoilPitchMin']
                parsed_weapon['recoilPitchMax'] = v['RecoilProperties']['recoilPitchMax']
                parsed_weapon['timeToTakeMin'] = v['RecoilProperties']['timeToTakeMin'] * 1000.0
                parsed_weapon['timeToTakeMax'] = v['RecoilProperties']['timeToTakeMax'] * 1000.0
                parsed_weapon['ADSScale'] = v['RecoilProperties']['ADSScale']
                parsed_weapon['movementPenalty'] = v['RecoilProperties']['movementPenalty']
                parsed_weapon['yawCurve'] = v['RecoilProperties']['yawCurve']['m_Curve']
                parsed_weapon['curvesAsScalar'] = v['RecoilProperties']['curvesAsScalar']
                parsed_weapon['useCurves'] =  v['RecoilProperties']['useCurves']
                parsed_weapon['shotsUntilMax'] = v['RecoilProperties']['shotsUntilMax']
                parsed_weapon['maxRecoilRadius'] = v['RecoilProperties']['maxRecoilRadius']

            if ("BaseProjectile" in v):
                parsed_weapon['repeatDelay'] = v['BaseProjectile']['repeatDelay'] * 1000.0
                parsed_weapon['automatic'] = v['BaseProjectile']['automatic']
                parsed_weapon['MagazineSize'] = v['BaseProjectile']['primaryMagazine']['definition']['builtInSize']
                parsed_weapon['stancePenaltyScale'] = v['BaseProjectile']['stancePenaltyScale']
                parsed_weapon['hasADS'] = v['BaseProjectile']['hasADS']

            if ("IronSights" in v):
                parsed_weapon['fieldOfViewOffset'] = v['IronSights']['fieldOfViewOffset']
                parsed_weapon['zoomFactor'] = v['IronSights']['zoomFactor']

            parsed_weapons.append(parsed_weapon)
        return parsed_weapons

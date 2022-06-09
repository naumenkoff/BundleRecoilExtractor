from audioop import avg
from animationcurve import *
import math

class DumpParser:
    
    def __init__(self, dump):
        
        # Store the dump
        self.dump = dump

    # Shitty impl of unity's Clamp01 func
    def clamp01(self, value):

        # Return the clamped value
        return max(min(value, 1.0), 0.0)

    def parse_attachments(self):
        
        # Will store attachments parsed from the dump
        parsed_attachments = []

        # Final processing for each attachment
        for k, v in self.dump['attachments'].items():

            # Will store the parsed data we need from the raw dump
            parsed_attachment = {'name': k, 'modifiers': {}}

            #
            # ProjectileWeaponMod
            #

            # Store the data
            parsed_attachment['modifiers'] = {
                'recoil'        : v['ProjectileWeaponMod']['recoil'],
                'repeat-delay'  : v['ProjectileWeaponMod']['repeatDelay']
            }
            
            #
            # IronSightOverride
            #

            # Check the mod has the IronSightsOverride entry
            if 'IronSightOverride' in v:

                # Store actual data.
                parsed_attachment['fov-bias']       = v['IronSightOverride']['fovBias']
                parsed_attachment['fov-offset']     = v['IronSightOverride']['fieldOfViewOffset']
                parsed_attachment['zoom-factor']    = v['IronSightOverride']['zoomFactor']

                # Store attachment type
                parsed_attachment['type']           = 'Scope'

            # Otherwise, fill with dummy data
            else:

                # Dummy data, you can filter this in your script.
                parsed_attachment['fov-bias']       = 0.0
                parsed_attachment['fov-offset']     = 0.0
                parsed_attachment['zoom-factor']    = 0.0
                
                # Store attachment type
                parsed_attachment['type']           = 'Barrel'
            
            # Store the parsed attachment in the output array
            parsed_attachments.append(parsed_attachment)
        
        # Return the final array
        return parsed_attachments

    def parse_weapons(self):

        # Will store weapons parsed from the dump
        parsed_weapons = []

        # Final processing for each weapon
        for k, v in self.dump['weapons'].items():
            
            # Will store the parsed data we need from the raw dump
            parsed_weapon = { 'name':k }

            #
            # BaseProjectile
            #
            parsed_weapon['repeat-delay']               = (v['BaseProjectile']['repeatDelay'] * 1000.0)
            parsed_weapon['is-automatic']               = v['BaseProjectile']['automatic']
            parsed_weapon['has-ads']                    = v['BaseProjectile']['hasADS']
            parsed_weapon['mag-cap']                    = v['BaseProjectile']['primaryMagazine']['definition']['builtInSize']
            parsed_weapon['stance-penalty']             = v['BaseProjectile']['stancePenaltyScale']

            #
            # IronSights
            #
            parsed_weapon['fov-offset']                 = v['IronSights']['fieldOfViewOffset']
            parsed_weapon['zoom-factor']                = v['IronSights']['zoomFactor']

            #
            # RecoilProperties
            #

            # Store non-related keys
            parsed_weapon['move-penalty']               = v['RecoilProperties']['movementPenalty']

            # Create the recoil key
            parsed_weapon['recoil'] = {}

            # Add recoil data
            parsed_weapon['recoil']['curves-as-scalar'] = v['RecoilProperties']['curvesAsScalar']
            parsed_weapon['recoil']['yaw-max']          = v['RecoilProperties']['recoilYawMax']
            parsed_weapon['recoil']['yaw-min']          = v['RecoilProperties']['recoilYawMin']
            parsed_weapon['recoil']['pitch-max']        = v['RecoilProperties']['recoilPitchMax']
            parsed_weapon['recoil']['pitch-min']        = v['RecoilProperties']['recoilPitchMin']
            parsed_weapon['recoil']['time-min']         = v['RecoilProperties']['timeToTakeMin'] * 1000.0
            parsed_weapon['recoil']['time-max']         = v['RecoilProperties']['timeToTakeMax'] * 1000.0
            parsed_weapon['recoil']['ads-scale']        = v['RecoilProperties']['ADSScale']
            parsed_weapon['recoil']['max-radius']       = v['RecoilProperties']['maxRecoilRadius']
            parsed_weapon['recoil']['shots-until-max']  = v['RecoilProperties']['shotsUntilMax']


            # Will store the curves for both AnimationCurve objects (pitch/yaw)
            parsed_weapon['recoil']['pitch-curve']      = []
            parsed_weapon['recoil']['yaw-curve']        = []

            # Build the yaw AnimationCurve object given the raw keyframe data.
            yaw_curve = AnimationCurve([KeyFrame(i['time'], i['value'], i['inSlope'], i['outSlope']) for i in v['RecoilProperties']['yawCurve']['m_Curve']])

            #
            # PitchCurves are never used.
            #

            # Determine the avg yaw between yaw/pitch-min/max, though I'm pretty sure the AddPunch values are always closer to the 'max' value.
            avg_yaw     = (parsed_weapon['recoil']['yaw-max'] + parsed_weapon['recoil']['yaw-min']) * 0.5
            avg_pitch   = (parsed_weapon['recoil']['pitch-max'] + parsed_weapon['recoil']['pitch-min']) * 0.5

            # This is kind of retarded, but idk a better way x)
            avg_yaw     = avg_yaw if not avg_yaw == 0.0 else parsed_weapon['recoil']['yaw-max']
            avg_pitch   = avg_pitch if not avg_pitch == 0.0 else parsed_weapon['recoil']['pitch-max']
            
            # Will store the current value we need to store. Needs to be put here for bounds check.
            store_yaw   = avg_yaw
            store_pitch = avg_pitch

            # Loop through the weapon's magazine
            for shots_fired in range(parsed_weapon['mag-cap']):

                # Check that we are using curves as scalar
                if parsed_weapon['recoil']['curves-as-scalar']:
                
                    # Determine the curve time for this bullet.
                    t           = self.clamp01(shots_fired / parsed_weapon['recoil']['shots-until-max'])

                    # Generate the value of the given yawCurve
                    store_yaw   = -avg_yaw
                    store_pitch = (-(avg_pitch * yaw_curve.evaluate(t)) * 0.5) # For some reason they use the yawCurve to modify the pitch values??? :D
                
                else:

                    # Store the values.
                    store_yaw   = -avg_yaw
                    store_pitch = -avg_pitch
                
                #
                # IF LINEAR WEAPONS ARE WONKY, PUT THIS CODE IN THE curvesAsScalar section.
                #

                # Perform a bounds check on pitch.
                if abs(store_pitch) > parsed_weapon['recoil']['max-radius']:
                    
                    # Just use half of max radius, however this value can NEVER be predicted.
                    store_pitch = parsed_weapon['recoil']['max-radius'] * 0.5

                # Store the values.
                parsed_weapon['recoil']['pitch-curve'].append(store_pitch)
                parsed_weapon['recoil']['yaw-curve'].append(store_yaw)

            # Append the parsed weapon to the list
            parsed_weapons.append(parsed_weapon)
        
        # Return parsed weapons
        return parsed_weapons
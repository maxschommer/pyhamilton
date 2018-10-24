#!python3

import os
import sys
sys.path.append("..\\")

from pyhamilton import (HamiltonInterface, LayoutManager, ResourceType, Tip96, Plate96,
    INITIALIZE, PICKUP, EJECT, ASPIRATE, DISPENSE,
    HamiltonError)

layfile = os.path.abspath(os.path.join('.', 'single_ch_aspirate_dispense.lay'))
lmgr = LayoutManager(layfile)
plate_type = ResourceType(Plate96, 'Cos_96_Rd_0001')
plate = lmgr.assign_unused_resource(plate_type)

tip_name_from_line = lambda line: LayoutManager.layline_first_field(line)
print(tip_name_from_line)
tip_name_condition = lambda line: LayoutManager.field_starts_with(tip_name_from_line(line), 'HTF_L_')
print(tip_name_condition)
tips_type = ResourceType(Tip96, tip_name_condition, tip_name_from_line)
print(tips_type)
tips = lmgr.assign_unused_resource(tips_type)
print(tips)
print(tips.layout_name())
print(tips.position_id(88))

if __name__ == '__main__':
    tip_no = 88 # top right corner
    well_no = 7 # bottom left corner
    tip_labware_pos = tips.layout_name() + ', ' + tips.position_id(tip_no) + ';'
    well_labware_pos = plate.layout_name() + ', ' + plate.position_id(well_no) + ';'
    liq_class = 'HighVolumeFilter_Water_DispenseJet_Empty'

    # tipSequence, labwarePositions, channelVariable, sequenceCounting, 2
    with HamiltonInterface() as hammy:
        hammy.wait_on_response(hammy.send_command(INITIALIZE, initializeAlways=0))
        ids = [hammy.send_command(PICKUP, False, {"tipSequence": "", "labwarePositions": tip_labware_pos, "channelVariable": "1111111100000000", "sequenceCounting": 0, "channelUse": 2}),
               hammy.send_command(ASPIRATE, labwarePositions=well_labware_pos, volumes=100.0, liquidClass=liq_class),
               hammy.send_command(DISPENSE, labwarePositions=well_labware_pos, volumes=100.0, liquidClass=liq_class),
               hammy.send_command(EJECT, labwarePositions=tip_labware_pos)]
        for id in ids:
            try:
                print(hammy.wait_on_response(id, raise_first_exception=True))
            except HamiltonError as he:
                print(he)

ci2had.py: Read FacialAnimation archive FACS files and output as Jin*.x3d and Menu.x3d

    Remove CoordinateInterpolaors and replace with HAnimDisplacers.

arroute.py: Read all Jin*.x3d files and create MultiFacialAnimationMenu.x3d
bigswitch.py: Read all Jin*.x3d files and create YehudiMenuJin.x3d
multihuman.py: Read all Jin*.x3d files and create MenuJin.x3d
singlehuman.py: Read all Jin*.x3d files and create SingleMenuJin.x3d

manyclocks2.py: Read all Jin*.x3d files and create ManyClocks.x3d

    Many TmeSensors
    ProximitySensor version
    rotating HUD
    Reset button doesn't reset other menu items

manyclocks.py : Read all Jin*.x3d files and create ManyClocks.x3d

    Current version
    Many TmeSensors
    Layer version, non-moving HUD
    Working Reset menu item
    Reset button doesn't untoggle

cleanup.py: Read ManyClocks.x3d, clean Displacers and produce CleanedYouClocks.x3d

    Cleaned current version

cleanwink.py: Read JinWink.x3d, produce CleanedWink.x3d
